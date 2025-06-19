import json
import os
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path
import logging

from app.models import TaskModel, TaskStatus, TaskPriority

logger = logging.getLogger(__name__)


class TaskStorage:
    def __init__(self, data_dir: Optional[str] = None):
        if data_dir is None:
            data_dir = os.path.expanduser("~/TODO")
        
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.tasks_file = self.data_dir / "tasks.json"
        
        # Initialize tasks file if it doesn't exist
        if not self.tasks_file.exists():
            self._save_tasks([])

    def _load_tasks(self) -> List[Dict[str, Any]]:
        """Load tasks from JSON file."""
        try:
            with open(self.tasks_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.warning(f"Could not load tasks: {e}")
            return []

    def _save_tasks(self, tasks: List[Dict[str, Any]]) -> None:
        """Save tasks to JSON file."""
        try:
            with open(self.tasks_file, 'w', encoding='utf-8') as f:
                json.dump(tasks, f, indent=2, ensure_ascii=False, default=str)
        except Exception as e:
            logger.error(f"Could not save tasks: {e}")
            raise

    def create_task(self, task_data: Dict[str, Any]) -> TaskModel:
        """Create a new task."""
        task_id = str(uuid.uuid4())
        task_data['id'] = task_id
        task_data['date_created'] = datetime.now()
        
        task = TaskModel(**task_data)
        
        tasks = self._load_tasks()
        tasks.append(task.model_dump())
        self._save_tasks(tasks)
        
        return task

    def get_task(self, task_id: str) -> Optional[TaskModel]:
        """Get a task by ID."""
        tasks = self._load_tasks()
        for task_data in tasks:
            if task_data.get('id') == task_id:
                return TaskModel(**task_data)
        return None

    def get_all_tasks(self, 
                     status: Optional[TaskStatus] = None,
                     priority: Optional[TaskPriority] = None,
                     tag: Optional[str] = None) -> List[TaskModel]:
        """Get all tasks with optional filtering."""
        tasks_data = self._load_tasks()
        tasks = [TaskModel(**task_data) for task_data in tasks_data]
        
        # Apply filters
        if status:
            tasks = [t for t in tasks if t.status == status]
        if priority:
            tasks = [t for t in tasks if t.priority == priority]
        if tag:
            tasks = [t for t in tasks if tag in t.tags]
        
        # Sort by creation date (newest first)
        tasks.sort(key=lambda x: x.date_created, reverse=True)
        return tasks

    def update_task(self, task_id: str, update_data: Dict[str, Any]) -> Optional[TaskModel]:
        """Update a task."""
        tasks = self._load_tasks()
        
        for i, task_data in enumerate(tasks):
            if task_data.get('id') == task_id:
                # Update fields
                for key, value in update_data.items():
                    if value is not None:
                        task_data[key] = value
                
                # Set completion date if status changed to completed
                if update_data.get('status') == TaskStatus.COMPLETED:
                    task_data['date_completed'] = datetime.now()
                
                tasks[i] = task_data
                self._save_tasks(tasks)
                return TaskModel(**task_data)
        
        return None

    def delete_task(self, task_id: str) -> bool:
        """Delete a task."""
        tasks = self._load_tasks()
        original_length = len(tasks)
        
        tasks = [t for t in tasks if t.get('id') != task_id]
        
        if len(tasks) < original_length:
            self._save_tasks(tasks)
            return True
        return False

    def get_stats(self) -> Dict[str, Any]:
        """Get task statistics."""
        tasks = self.get_all_tasks()
        
        stats = {
            'total': len(tasks),
            'by_status': {},
            'by_priority': {},
            'overdue': 0
        }
        
        for status in TaskStatus:
            stats['by_status'][status.value] = len([t for t in tasks if t.status == status])
        
        for priority in TaskPriority:
            stats['by_priority'][priority.value] = len([t for t in tasks if t.priority == priority])
        
        # Count overdue tasks
        today = datetime.now().date()
        stats['overdue'] = len([
            t for t in tasks 
            if t.date_by and t.date_by < today and t.status != TaskStatus.COMPLETED
        ])
        
        return stats