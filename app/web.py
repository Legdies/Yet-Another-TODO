from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
import logging

from app.models import TaskStatus, TaskPriority
from app.storage import TaskStorage

logger = logging.getLogger(__name__)
router = APIRouter(tags=["web"])
templates = Jinja2Templates(directory="templates")

# Initialize storage
storage = TaskStorage()


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page with task list."""
    try:
        tasks = storage.get_all_tasks()
        stats = storage.get_stats()
        
        return templates.TemplateResponse("index.html", {
            "request": request,
            "tasks": tasks,
            "stats": stats,
            "task_statuses": TaskStatus,
            "task_priorities": TaskPriority
        })
    except Exception as e:
        logger.error(f"Error loading home page: {e}")
        raise HTTPException(status_code=500, detail="Failed to load tasks")


@router.get("/create", response_class=HTMLResponse)
async def create_task_form(request: Request):
    """Create task form."""
    return templates.TemplateResponse("create_task.html", {
        "request": request,
        "task_priorities": TaskPriority
    })


@router.post("/create")
async def create_task_submit(
    request: Request,
    name: str = Form(...),
    description: Optional[str] = Form(None),
    priority: TaskPriority = Form(TaskPriority.MEDIUM),
    date_by: Optional[str] = Form(None),
    tags: Optional[str] = Form(None)
):
    """Handle task creation form submission."""
    try:
        task_data = {
            "name": name,
            "description": description or "",
            "priority": priority,
        }
        
        if date_by:
            from datetime import datetime
            task_data["date_by"] = datetime.strptime(date_by, "%Y-%m-%d").date()
        
        if tags:
            task_data["tags"] = [tag.strip() for tag in tags.split(",") if tag.strip()]
        
        storage.create_task(task_data)
        return RedirectResponse(url="/", status_code=303)
        
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        return templates.TemplateResponse("create_task.html", {
            "request": request,
            "error": "Failed to create task",
            "task_priorities": TaskPriority
        })


@router.get("/task/{task_id}", response_class=HTMLResponse)
async def view_task(request: Request, task_id: str):
    """View individual task."""
    task = storage.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return templates.TemplateResponse("task_detail.html", {
        "request": request,
        "task": task,
        "task_statuses": TaskStatus,
        "task_priorities": TaskPriority
    })


@router.post("/task/{task_id}/update")
async def update_task_submit(
    request: Request,
    task_id: str,
    status: Optional[TaskStatus] = Form(None),
    priority: Optional[TaskPriority] = Form(None),
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None)
):
    """Handle task update form submission."""
    try:
        update_data = {}
        if status:
            update_data["status"] = status
        if priority:
            update_data["priority"] = priority
        if name:
            update_data["name"] = name
        if description is not None:
            update_data["description"] = description
        
        task = storage.update_task(task_id, update_data)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return RedirectResponse(url=f"/task/{task_id}", status_code=303)
        
    except Exception as e:
        logger.error(f"Error updating task: {e}")
        raise HTTPException(status_code=500, detail="Failed to update task")


@router.post("/task/{task_id}/delete")
async def delete_task_submit(task_id: str):
    """Handle task deletion."""
    try:
        success = storage.delete_task(task_id)
        if not success:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return RedirectResponse(url="/", status_code=303)
        
    except Exception as e:
        logger.error(f"Error deleting task: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete task")