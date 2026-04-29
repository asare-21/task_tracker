from pathlib import Path
import json
from model import Task
from datetime import datetime

class TaskStorage:
    def __init__(self, storage_file="task.json"):
        self.storage_file = Path(storage_file)
        self.create_task_storage_file()
        self.list_task_status()

    def create_task_storage_file(self):        
        if not self.storage_file.exists():
            with self.storage_file.open("w") as f:
                json.dump([], f)
                

    def list_task_status(self):
        with self.storage_file.open("r") as f:
            tasks = json.load(f)
            
            completed_tasks = [Task(**task) for task in tasks if task["completed"]]
            pending_tasks = [Task(**task) for task in tasks if not task["completed"]]
            
            print(f"Completed Tasks ✅: {len(completed_tasks)}")
            print(f"Pending Tasks ❌: {len(pending_tasks)}")
            
    def list_tasks(self):
        with self.storage_file.open("r") as f:
            tasks = json.load(f)
            print(tasks)
            return [Task(**task) for task in tasks]
            
    def add_task(self, description: str):
        with self.storage_file.open("r") as f:
            tasks = json.load(f)
            
        # TODO: Add error handling for empty descriptions
        if not description:
            print("Task description cannot be empty. ❌")
            return
        
        new_task = Task(id=len(tasks) + 1, description=description, completed=False)
        tasks.append(new_task.model_dump())
        
        with self.storage_file.open("w") as f:
            json.dump(tasks, f, indent=4)
            
    
    def complete_task(self, task_id: int):
        with self.storage_file.open("r") as f:
            tasks = json.load(f)
        
        for task in tasks:
            if task["id"] == task_id:
                task["completed"] = True
                task["completed_at"] = datetime.now().isoformat()
                break

        
        with self.storage_file.open("w") as f:
            json.dump(tasks, f, indent=4)


    def delete_task(self, task_id: int):
        with self.storage_file.open("r") as f:
            tasks = json.load(f)
        
        tasks = [task for task in tasks if task["id"] != task_id]
        # Add error handling for invalid task IDs
        if not tasks:
            print("No tasks found with the given ID. 👀")
            return
        
        with self.storage_file.open("w") as f:
            json.dump(tasks, f, indent=4)
