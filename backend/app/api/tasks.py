from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, BackgroundTasks
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
        "hosts": hosts_status
    }

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
