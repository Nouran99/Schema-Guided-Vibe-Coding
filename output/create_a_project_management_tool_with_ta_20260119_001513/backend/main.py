from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
import uuid

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

projects = {}
tasks = {}
users = {"1": {"id": "1", "username": "alice", "email": "alice@example.com"},
         "2": {"id": "2", "username": "bob", "email": "bob@example.com"}}

class ProjectCreate(BaseModel):
    name: str

class TaskCreate(BaseModel):
    title: str
    description: str
    project_id: str
    assignee_id: Optional[str] = None
    deadline: Optional[datetime] = None

class TaskUpdate(BaseModel):
    status: Optional[str] = None
    assignee_id: Optional[str] = None
    deadline: Optional[datetime] = None

@app.post("/api/projects")
def create_project(project: ProjectCreate):
    project_id = str(uuid.uuid4())
    projects[project_id] = {
        "id": project_id,
        "name": project.name,
        "created_at": datetime.now(),
        "progress_percentage": 0.0
    }
    return projects[project_id]

@app.get("/api/projects")
def get_projects():
    return list(projects.values())

@app.post("/api/projects/{project_id}/tasks")
def add_task(project_id: str, task: TaskCreate):
    if project_id not in projects:
        raise HTTPException(status_code=404, detail="Project not found")
    task_id = str(uuid.uuid4())
    tasks[task_id] = {
        "id": task_id,
        "title": task.title,
        "description": task.description,
        "status": "todo",
        "deadline": task.deadline,
        "project_id": project_id,
        "assignee_id": task.assignee_id
    }
    return tasks[task_id]

@app.put("/api/tasks/{task_id}")
def update_task(task_id: str, updates: TaskUpdate):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    if updates.status:
        if updates.status not in ["todo", "in_progress", "done"]:
            raise HTTPException(status_code=400, detail="Invalid status")
        tasks[task_id]["status"] = updates.status
    if updates.assignee_id is not None:
        tasks[task_id]["assignee_id"] = updates.assignee_id
    if updates.deadline is not None:
        tasks[task_id]["deadline"] = updates.deadline
    return tasks[task_id]

@app.get("/api/tasks")
def get_tasks(assignee_id: Optional[str] = None, project_id: Optional[str] = None):
    filtered_tasks = list(tasks.values())
    if assignee_id:
        filtered_tasks = [t for t in filtered_tasks if t["assignee_id"] == assignee_id]
    if project_id:
        filtered_tasks = [t for t in filtered_tasks if t["project_id"] == project_id]
    for task in filtered_tasks:
        if task["deadline"] and task["deadline"] < datetime.now() and task["status"] != "done":
            task["overdue"] = True
        else:
            task["overdue"] = False
    return filtered_tasks

@app.get("/api/projects/{project_id}/tasks")
def get_project_tasks(project_id: str):
    if project_id not in projects:
        raise HTTPException(status_code=404, detail="Project not found")
    project_tasks = [t for t in tasks.values() if t["project_id"] == project_id]
    done_count = sum(1 for t in project_tasks if t["status"] == "done")
    total = len(project_tasks)
    progress = (done_count / total * 100) if total > 0 else 0.0
    projects[project_id]["progress_percentage"] = progress
    return project_tasks

@app.delete("/api/tasks/{task_id}")
def delete_task(task_id: str):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    del tasks[task_id]
    return {"message": "Task deleted"}

@app.get("/api/users")
def get_users():
    return list(users.values())