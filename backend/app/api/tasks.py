from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from ..db import get_db
from ..models import Task, TaskHost, TaskMode, BatchFailStrategy, TaskHostStatus
from ..task_runner import run_task, task_event_bus
import asyncio

router = APIRouter(prefix="/tasks", tags=["tasks"])

class CreateTaskReq(BaseModel):
    name: str
    command: str
    host_ids: List[int]
    mode: TaskMode = TaskMode.broadcast
    batch_size: Optional[int] = None
    batch_interval: Optional[int] = None
    on_batch_fail_strategy: Optional[BatchFailStrategy] = None

@router.get("/", response_model=List[dict])
def list_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    tasks = db.query(Task).order_by(Task.created_at.desc()).offset(skip).limit(limit).all()
    result = []
    for t in tasks:
        total = len(t.task_hosts)
        success = sum(1 for th in t.task_hosts if th.status == TaskHostStatus.success)
        failed = sum(1 for th in t.task_hosts if th.status in [TaskHostStatus.failed, TaskHostStatus.cancelled])
        running = sum(1 for th in t.task_hosts if th.status == TaskHostStatus.running)
        
        # Calculate progress percentage
        progress = 0
        if total > 0:
            completed = success + failed
            progress = int((completed / total) * 100)
            
        status = "running"
        if total > 0 and (success + failed) == total:
            status = "completed"
            
        result.append({
            "id": t.id,
            "name": t.name,
            "command": t.command,
            "mode": t.mode,
            "created_at": t.created_at,
            "host_count": total,
            "success_count": success,
            "failed_count": failed,
            "progress": progress,
            "status": status
        })
    return result

@router.post("/", response_model=dict)
def create_task(req: CreateTaskReq, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    task = Task(
        name=req.name,
        command=req.command,
        mode=req.mode,
        batch_size=req.batch_size,
        batch_interval=req.batch_interval,
        on_batch_fail_strategy=req.on_batch_fail_strategy,
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    for host_id in req.host_ids:
        th = TaskHost(task_id=task.id, host_id=host_id)
        db.add(th)
    
    db.commit()

    # Trigger async task execution
    background_tasks.add_task(run_task, task.id)

    return {"task_id": task.id}

@router.get("/{task_id}", response_model=dict)
def get_task_details(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        return {}
    
    hosts_status = []
    for th in task.task_hosts:
        hosts_status.append({
            "host_id": th.host_id,
            "status": th.status,
            "exit_code": th.exit_code,
            "error": th.error
        })

    return {
        "id": task.id,
        "name": task.name,
        "mode": task.mode,
        "created_at": task.created_at,
        "hosts": hosts_status
    }

@router.post("/{task_id}/run", response_model=dict)
def run_task_again(task_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Create a new task based on the old one
    new_task = Task(
        name=f"{task.name} (Rerun)",
        command=task.command,
        mode=task.mode,
        batch_size=task.batch_size,
        batch_interval=task.batch_interval,
        on_batch_fail_strategy=task.on_batch_fail_strategy,
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    # Copy hosts
    for th in task.task_hosts:
        new_th = TaskHost(task_id=new_task.id, host_id=th.host_id)
        db.add(new_th)
    
    db.commit()

    # Trigger async task execution
    background_tasks.add_task(run_task, new_task.id)

    return {"task_id": new_task.id}

@router.websocket("/{task_id}/stream")
async def task_stream(websocket: WebSocket, task_id: int):
    await websocket.accept()
    
    async def log_handler(msg: dict):
        if str(msg.get("task_id")) == str(task_id):
            try:
                await websocket.send_json(msg)
            except:
                pass

    task_event_bus.subscribe(log_handler)
    
    try:
        while True:
            # Keep connection open
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        task_event_bus.unsubscribe(log_handler)
