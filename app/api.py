from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
import logging

from app.models import (
    TaskModel, TaskCreateRequest, TaskUpdateRequest, 
    TaskListResponse, APIResponse, TaskStatus, TaskPriority
)
from app.storage import TaskStorage

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["tasks"])

# Initialize storage
storage = TaskStorage()


@router.post("/tasks", response_model=APIResponse)
async def create_task(task_request: TaskCreateRequest):
    """Create a new task."""
    try:
        task = storage.create_task(task_request.model_dump())
        return APIResponse(
            success=True,
            message="Task created successfully",
            data=task.model_dump()
        )
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        raise HTTPException(status_code=500, detail="Failed to create task")


@router.get("/tasks", response_model=TaskListResponse)
async def get_tasks(
    status: Optional[TaskStatus] = Query(None, description="Filter by status"),
    priority: Optional[TaskPriority] = Query(None, description="Filter by priority"),
    tag: Optional[str] = Query(None, description="Filter by tag")
):
    """Get all tasks with optional filtering."""
    try:
        tasks = storage.get_all_tasks(status=status, priority=priority, tag=tag)
        all_tasks = storage.get_all_tasks()
        
        return TaskListResponse(
            tasks=tasks,
            total=len(all_tasks),
            filtered=len(tasks)
        )
    except Exception as e:
        logger.error(f"Error getting tasks: {e}")
        raise HTTPException(status_code=500, detail="Failed to get tasks")


@router.get("/tasks/{task_id}", response_model=APIResponse)
async def get_task(task_id: str):
    """Get a specific task by ID."""
    task = storage.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return APIResponse(
        success=True,
        message="Task retrieved successfully",
        data=task.model_dump()
    )


@router.put("/tasks/{task_id}", response_model=APIResponse)
async def update_task(task_id: str, task_update: TaskUpdateRequest):
    """Update a task."""
    try:
        # Filter out None values
        update_data = {k: v for k, v in task_update.model_dump().items() if v is not None}
        
        task = storage.update_task(task_id, update_data)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return APIResponse(
            success=True,
            message="Task updated successfully",
            data=task.model_dump()
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating task: {e}")
        raise HTTPException(status_code=500, detail="Failed to update task")


@router.delete("/tasks/{task_id}", response_model=APIResponse)
async def delete_task(task_id: str):
    """Delete a task."""
    try:
        success = storage.delete_task(task_id)
        if not success:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return APIResponse(
            success=True,
            message="Task deleted successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting task: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete task")


@router.get("/stats", response_model=APIResponse)
async def get_stats():
    """Get task statistics."""
    try:
        stats = storage.get_stats()
        return APIResponse(
            success=True,
            message="Statistics retrieved successfully",
            data=stats
        )
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get statistics")