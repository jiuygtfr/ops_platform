import asyncio
from typing import List, Callable
from sqlalchemy.orm import Session
from .models import Task, TaskHost, TaskHostStatus, Host, BatchFailStrategy
from .db import SessionLocal
import asyncssh

# Global event bus for task logs (Simple in-memory implementation)
# In production, use Redis Pub/Sub
class TaskEventBus:
    def __init__(self):
        self.subscribers: List[Callable] = []

    def subscribe(self, callback: Callable):
        self.subscribers.append(callback)

    def unsubscribe(self, callback: Callable):
        if callback in self.subscribers:
            self.subscribers.remove(callback)

    async def publish(self, message: dict):
        for sub in self.subscribers:
            if asyncio.iscoroutinefunction(sub):
                await sub(message)
            else:
                sub(message)

task_event_bus = TaskEventBus()

async def execute_command_on_host(task_id: int, task_host_id: int, host_ip: str, host_port: int, host_user: str, host_pass: str, command: str):
    db: Session = SessionLocal()
    task_host = db.query(TaskHost).get(task_host_id)
    if not task_host:
        db.close()
        return

    try:
        task_host.status = TaskHostStatus.running
        db.commit()
        
        await task_event_bus.publish({
            "task_id": task_id,
            "host_id": task_host.host_id,
            "status": "running",
            "line": f"--- Start executing on {host_ip} ---"
        })

        async with asyncssh.connect(host_ip, port=host_port, username=host_user, password=host_pass, known_hosts=None) as conn:
            result = await conn.run(command)
            
            # Send stdout
            if result.stdout:
                await task_event_bus.publish({
                    "task_id": task_id,
                    "host_id": task_host.host_id,
                    "status": "running",
                    "line": result.stdout
                })
            
            # Send stderr
            if result.stderr:
                await task_event_bus.publish({
                    "task_id": task_id,
                    "host_id": task_host.host_id,
                    "status": "running",
                    "line": result.stderr
                })

            task_host.exit_code = result.exit_status
            task_host.status = TaskHostStatus.success if result.exit_status == 0 else TaskHostStatus.failed
            
            await task_event_bus.publish({
                "task_id": task_id,
                "host_id": task_host.host_id,
                "status": task_host.status.value,
                "line": f"--- Finished with exit code {result.exit_status} ---"
            })

    except Exception as e:
        task_host.status = TaskHostStatus.failed
        task_host.error = str(e)
        await task_event_bus.publish({
            "task_id": task_id,
            "host_id": task_host.host_id,
            "status": "failed",
            "line": f"Error: {str(e)}"
        })
    finally:
        db.commit()
        db.close()

async def run_task(task_id: int, concurrency: int = 5):
    db: Session = SessionLocal()
    task = db.query(Task).get(task_id)
    if not task:
        db.close()
        return

    task_hosts = db.query(TaskHost).filter(TaskHost.task_id == task_id).all()
    
    # Prepare host info to avoid db session issues in async
    hosts_info = []
    for th in task_hosts:
        host = db.query(Host).get(th.host_id)
        hosts_info.append({
            "task_host_id": th.id,
            "host_id": host.id,
            "ip": host.ip,
            "port": host.ssh_port,
            "username": host.username,
            "password": host.password,
            "auth_type": host.auth_type
        })
    
    db.close()

    batch_size = task.batch_size if task.mode == "batch" and task.batch_size else len(hosts_info)
    batches = [hosts_info[i:i + batch_size] for i in range(0, len(hosts_info), batch_size)]

    for batch in batches:
        sem = asyncio.Semaphore(concurrency)
        tasks = []

        async def worker(info):
            async with sem:
                # We assume password auth for simplicity in this demo
                await execute_command_on_host(
                    task_id, 
                    info["task_host_id"], 
                    info["ip"], 
                    info["port"], 
                    info["username"], 
                    info["password"], 
                    task.command
                )

        for info in batch:
            tasks.append(asyncio.create_task(worker(info)))

        await asyncio.gather(*tasks)

        # Check for failures if strategy is pause_on_fail
        if task.on_batch_fail_strategy == BatchFailStrategy.pause_on_fail:
            # Re-check status from DB
            db_check = SessionLocal()
            has_failure = db_check.query(TaskHost).filter(
                TaskHost.task_id == task_id,
                TaskHost.host_id.in_([h["host_id"] for h in batch]),
                TaskHost.status == TaskHostStatus.failed
            ).count() > 0
            db_check.close()
            
            if has_failure:
                await task_event_bus.publish({
                    "task_id": task_id,
                    "status": "paused",
                    "line": "--- Batch failed, pausing task ---"
                })
                break

        if task.batch_interval and task.batch_interval > 0:
            await asyncio.sleep(task.batch_interval)
