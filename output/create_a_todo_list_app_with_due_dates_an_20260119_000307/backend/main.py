from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
import uuid

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

tasks_db = {}

class TaskCreate(BaseModel):
    title: str
    due_date: Optional[datetime] = None
    priority: str = "medium"

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: Optional[str] = None

class Task(TaskCreate):
    id: str
    is_complete: bool = False
    created_at: datetime

@app.get("/api/tasks")
def get_tasks(priority: Optional[str] = None, sort: Optional[str] = None):
    tasks = list(tasks_db.values())
    if priority and priority in ["high", "medium", "low"]:
        tasks = [t for t in tasks if t.priority == priority]
    if sort == "due_date":
        tasks.sort(key=lambda x: (x.due_date is None, x.due_date))
    return tasks

@app.post("/api/tasks")
def create_task(task: TaskCreate):
    if task.priority not in ["high", "medium", "low"]:
        raise HTTPException(status_code=400, detail="Priority must be high, medium, or low")
    task_id = str(uuid.uuid4())
    new_task = Task(
        id=task_id,
        title=task.title,
        due_date=task.due_date,
        priority=task.priority,
        created_at=datetime.now()
    )
    tasks_db[task_id] = new_task
    return new_task

@app.put("/api/tasks/{task_id}")
def update_task(task_id: str, task_update: TaskUpdate):
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    task = tasks_db[task_id]
    if task_update.title is not None:
        task.title = task_update.title
    if task_update.due_date is not None:
        task.due_date = task_update.due_date
    if task_update.priority is not None:
        if task_update.priority not in ["high", "medium", "low"]:
            raise HTTPException(status_code=400, detail="Priority must be high, medium, or low")
        task.priority = task_update.priority
    return task

@app.patch("/api/tasks/{task_id}/complete")
def mark_complete(task_id: str):
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    tasks_db[task_id].is_complete = True
    return tasks_db[task_id]

@app.delete("/api/tasks/{task_id}")
def delete_task(task_id: str):
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    del tasks_db[task_id]
    return {"message": "Task deleted"}
