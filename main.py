from storage import TaskStorage
import cmd
from rich.table import Table
from rich.console import Console


class TaskCLI(cmd.Cmd):
    intro = "Welcome to the Task Tracker CLI! Type help or ? to list commands.\n"
    prompt = "(task-tracker) "
    
    def __init__(self):
        super().__init__()
        self.storage = TaskStorage()

    def do_add(self,arg ):
        """Add a new task to the task tracker."""
        self.storage.add_task(arg)
        print("Task added successfully ✅")
        
    def do_complete(self, arg):
        """Complete a task by its ID."""
        try:
            task_id = int(arg)
            self.storage.complete_task(task_id)
        except ValueError:
            print("Invalid task ID. Please enter a number.")
            
    def do_list(self, _):
        """List all tasks and their status."""
        tasks = self.storage.list_tasks()

        if not tasks:
            print("No tasks found.")
            return

        console = Console()
        table = Table(title="Task List")

        table.add_column("ID",           style="cyan",  no_wrap=True)
        table.add_column("Description",  style="white")
        table.add_column("Status",       style="green")
        table.add_column("Completed At", style="magenta")

        for task in tasks:
            status       = "✅ Done"    if task.completed else "⏳ Pending"
            completed_at = str(task.completed_at) if task.completed_at else "—"

            table.add_row(
                str(task.id),
                task.description,
                status,
                completed_at
            )

        console.print(table)
        

    def do_delete(self, arg):
        """Delete a task by its ID."""
        try:
            task_id = int(arg)
            self.storage.delete_task(task_id)
            print("Task deleted successfully ✅")
        except ValueError:
            print("Invalid task ID. Please enter a number.")
            
    def do_update(self,arg ):
        """Update a task's description by its ID."""
        try:
            task_id = int(arg)
            new_description = input("Enter new task description: ")
            self.storage.update_task(task_id, new_description)
            print("Task updated successfully ✅")
        except ValueError:
            print("Invalid task ID. Please enter a number.")
            
    def do_quit(self, arg):
        """Exit the Task Tracker CLI."""
        print("Goodbye! 👋")
        return True
            

TaskCLI().cmdloop()