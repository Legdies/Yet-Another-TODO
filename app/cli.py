import os
import sys
from typing import Optional
import logging
from datetime import datetime, date

from app.storage import TaskStorage
from app.models import TaskStatus, TaskPriority

logger = logging.getLogger(__name__)


class TodoCLI:
    def __init__(self, data_dir: Optional[str] = None):
        self.storage = TaskStorage(data_dir)
        self.running = True

    def clear_screen(self):
        """Clear the terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_header(self):
        """Print application header."""
        print("=" * 50)
        print("Yet Another TODO - CLI Interface v0.2.0")
        print("=" * 50)
        print()

    def print_menu(self):
        """Print main menu options."""
        print("Main Menu:")
        print("1. List all tasks")
        print("2. Create new task")
        print("3. View task details")
        print("4. Update task")
        print("5. Delete task")
        print("6. Show statistics")
        print("0. Exit")
        print()

    def list_tasks(self, status_filter: Optional[TaskStatus] = None):
        """List all tasks with optional status filter."""
        tasks = self.storage.get_all_tasks(status=status_filter)
        
        if not tasks:
            print("No tasks found.")
            return

        print(f"\n{'ID':<8} {'Name':<30} {'Status':<12} {'Priority':<10} {'Due Date':<12}")
        print("-" * 80)
        
        for task in tasks:
            due_date = task.date_by.strftime("%Y-%m-%d") if task.date_by else "No due date"
            print(f"{task.id[:8]:<8} {task.name[:30]:<30} {task.status.value:<12} "
                  f"{task.priority.value:<10} {due_date:<12}")

    def create_task(self):
        """Create a new task interactively."""
        print("\nCreate New Task")
        print("-" * 20)
        
        name = input("Task name: ").strip()
        if not name:
            print("Task name is required!")
            return

        description = input("Description (optional): ").strip()
        
        print("\nPriority options:")
        for i, priority in enumerate(TaskPriority, 1):
            print(f"{i}. {priority.value}")
        
        try:
            priority_choice = int(input("Select priority (1-4): ")) - 1
            priority = list(TaskPriority)[priority_choice]
        except (ValueError, IndexError):
            priority = TaskPriority.MEDIUM
            print("Invalid choice, using MEDIUM priority")

        due_date_str = input("Due date (YYYY-MM-DD, optional): ").strip()
        due_date = None
        if due_date_str:
            try:
                due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
            except ValueError:
                print("Invalid date format, skipping due date")

        tags_str = input("Tags (comma-separated, optional): ").strip()
        tags = [tag.strip() for tag in tags_str.split(",") if tag.strip()] if tags_str else []

        task_data = {
            "name": name,
            "description": description,
            "priority": priority,
            "date_by": due_date,
            "tags": tags
        }

        try:
            task = self.storage.create_task(task_data)
            print(f"\nTask created successfully! ID: {task.id}")
        except Exception as e:
            print(f"Error creating task: {e}")

    def view_task(self):
        """View detailed information about a specific task."""
        task_id = input("Enter task ID (or first 8 characters): ").strip()
        if not task_id:
            return

        # Try to find task by partial ID
        all_tasks = self.storage.get_all_tasks()
        matching_tasks = [t for t in all_tasks if t.id.startswith(task_id)]
        
        if not matching_tasks:
            print("Task not found!")
            return
        
        if len(matching_tasks) > 1:
            print("Multiple tasks match that ID. Please be more specific:")
            for task in matching_tasks:
                print(f"  {task.id[:8]} - {task.name}")
            return

        task = matching_tasks[0]
        
        print(f"\nTask Details:")
        print(f"ID: {task.id}")
        print(f"Name: {task.name}")
        print(f"Description: {task.description or 'No description'}")
        print(f"Status: {task.status.value}")
        print(f"Priority: {task.priority.value}")
        print(f"Created: {task.date_created.strftime('%Y-%m-%d %H:%M')}")
        print(f"Due Date: {task.date_by.strftime('%Y-%m-%d') if task.date_by else 'No due date'}")
        print(f"Completed: {task.date_completed.strftime('%Y-%m-%d %H:%M') if task.date_completed else 'Not completed'}")
        print(f"Tags: {', '.join(task.tags) if task.tags else 'No tags'}")

    def update_task(self):
        """Update an existing task."""
        task_id = input("Enter task ID to update: ").strip()
        if not task_id:
            return

        # Find task by partial ID
        all_tasks = self.storage.get_all_tasks()
        matching_tasks = [t for t in all_tasks if t.id.startswith(task_id)]
        
        if not matching_tasks:
            print("Task not found!")
            return
        
        if len(matching_tasks) > 1:
            print("Multiple tasks match that ID. Please be more specific.")
            return

        task = matching_tasks[0]
        print(f"\nUpdating task: {task.name}")
        
        # Status update
        print("\nStatus options:")
        for i, status in enumerate(TaskStatus, 1):
            print(f"{i}. {status.value}")
        
        status_choice = input(f"Select new status (current: {task.status.value}, press Enter to skip): ").strip()
        new_status = None
        if status_choice:
            try:
                new_status = list(TaskStatus)[int(status_choice) - 1]
            except (ValueError, IndexError):
                print("Invalid choice, keeping current status")

        update_data = {}
        if new_status:
            update_data["status"] = new_status

        try:
            updated_task = self.storage.update_task(task.id, update_data)
            if updated_task:
                print("Task updated successfully!")
            else:
                print("Failed to update task")
        except Exception as e:
            print(f"Error updating task: {e}")

    def delete_task(self):
        """Delete a task."""
        task_id = input("Enter task ID to delete: ").strip()
        if not task_id:
            return

        # Find task by partial ID
        all_tasks = self.storage.get_all_tasks()
        matching_tasks = [t for t in all_tasks if t.id.startswith(task_id)]
        
        if not matching_tasks:
            print("Task not found!")
            return
        
        if len(matching_tasks) > 1:
            print("Multiple tasks match that ID. Please be more specific.")
            return

        task = matching_tasks[0]
        confirm = input(f"Are you sure you want to delete '{task.name}'? (y/N): ").strip().lower()
        
        if confirm == 'y':
            try:
                success = self.storage.delete_task(task.id)
                if success:
                    print("Task deleted successfully!")
                else:
                    print("Failed to delete task")
            except Exception as e:
                print(f"Error deleting task: {e}")

    def show_statistics(self):
        """Show task statistics."""
        stats = self.storage.get_stats()
        
        print("\nTask Statistics:")
        print("-" * 20)
        print(f"Total tasks: {stats['total']}")
        print(f"Overdue tasks: {stats['overdue']}")
        
        print("\nBy Status:")
        for status, count in stats['by_status'].items():
            print(f"  {status}: {count}")
        
        print("\nBy Priority:")
        for priority, count in stats['by_priority'].items():
            print(f"  {priority}: {count}")

    def run(self):
        """Main CLI loop."""
        while self.running:
            self.clear_screen()
            self.print_header()
            self.print_menu()
            
            try:
                choice = input("Enter your choice: ").strip()
                
                if choice == '0':
                    self.running = False
                    print("Goodbye!")
                elif choice == '1':
                    self.list_tasks()
                elif choice == '2':
                    self.create_task()
                elif choice == '3':
                    self.view_task()
                elif choice == '4':
                    self.update_task()
                elif choice == '5':
                    self.delete_task()
                elif choice == '6':
                    self.show_statistics()
                else:
                    print("Invalid choice! Please try again.")
                
                if self.running:
                    input("\nPress Enter to continue...")
                    
            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"An error occurred: {e}")
                input("Press Enter to continue...")


def main():
    """CLI entry point."""
    cli = TodoCLI()
    cli.run()


if __name__ == "__main__":
    main()