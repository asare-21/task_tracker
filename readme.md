# Task Tracker CLI

A command-line task manager built with Python. Keeps your to-do list in a local JSON file and gives you a clean, color-coded table view powered by [Rich](https://github.com/Textualize/rich).

---

## Features

- Add, update, delete, and complete tasks
- Persistent storage via a local `task.json` file
- Rich table display with task ID, description, status, and completion timestamp
- Live summary of completed vs. pending tasks on startup

---

## Requirements

- Python 3.9+
- Dependencies listed in `requirements.txt`

---

## Installation

1. Clone the repository:

```bash
git clone <repo-url>
cd task_tracker
```

1. Create and activate a virtual environment:

```bash
python -m venv .env
source .env/bin/activate      # macOS/Linux
.env\Scripts\activate         # Windows
```

1. Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Usage

Start the interactive CLI:

```bash
python main.py
```

You will be greeted with a summary of your current tasks and dropped into an interactive prompt:

```bash
Completed Tasks ✅: 2
Pending Tasks ❌: 1
Welcome to the Task Tracker CLI! Type help or ? to list commands.

(task-tracker)
```

---

## Commands

| Command              | Description                                      |
|----------------------|--------------------------------------------------|
| `add <description>`  | Add a new task with the given description        |
| `list`               | Display all tasks in a formatted table           |
| `complete <id>`      | Mark a task as completed by its ID               |
| `update <id>`        | Update a task's description by its ID            |
| `delete <id>`        | Delete a task by its ID                          |
| `help` or `?`        | List all available commands                      |
| `quit`               | Exit the CLI                                     |

---

## Examples

```bash
(task-tracker) add Buy groceries
Task added successfully ✅

(task-tracker) list
              Task List
┌────┬────────────────┬───────────┬──────────────────────┐
│ ID │ Description    │ Status    │ Completed At         │
├────┼────────────────┼───────────┼──────────────────────┤
│ 1  │ Buy groceries  │ ⏳ Pending │ —                    │
└────┴────────────────┴───────────┴──────────────────────┘

(task-tracker) complete 1
(task-tracker) list
              Task List
┌────┬────────────────┬───────────┬──────────────────────────┐
│ ID │ Description    │ Status    │ Completed At             │
├────┼────────────────┼───────────┼──────────────────────────┤
│ 1  │ Buy groceries  │ ✅ Done   │ 29 Apr 2026, 14:32       │
└────┴────────────────┴───────────┴──────────────────────────┘

(task-tracker) delete 1
Task deleted successfully ✅

(task-tracker) quit
Goodbye! 👋
```

---

## Testing

The project uses [pytest](https://docs.pytest.org/) for unit tests. Tests run against temporary files so your real `task.json` is never touched.

### Run all tests

```bash
pytest test_task_tracker.py
```

### Run with verbose output

```bash
pytest test_task_tracker.py -v
```

### Run a specific test class

```bash
pytest test_task_tracker.py::TestAddTask -v
```

### Test coverage

| Class | What it covers |
|---|---|
| `TestTaskModel` | Task creation, defaults, serialisation, and round-trip from dict |
| `TestStorageInit` | File creation on first run; existing data is not overwritten |
| `TestAddTask` | Adding tasks, ID auto-increment, empty description rejection |
| `TestListTasks` | Listing tasks from an empty or populated store |
| `TestCompleteTask` | Marking tasks done, timestamp validation, no-op on bad ID |
| `TestDeleteTask` | Deleting by ID, no-op on bad ID, known bug with last task |
| `TestListTaskStatus` | Printed summary counts for completed vs. pending tasks |

> **Known bug documented in tests:** deleting the only remaining task is currently a no-op due to a premature `if not tasks: return` guard in `storage.py`. The `test_delete_last_task_bug` test captures this behaviour.

---

## Project Structure

```bash
task_tracker/
├── main.py               # CLI entry point and command definitions
├── model.py              # Pydantic Task model
├── storage.py            # JSON read/write logic
├── test_task_tracker.py  # pytest test suite
├── task.json             # Persistent task data (auto-created on first run)
└── requirements.txt      # Python dependencies
```

---

## Data Storage

Tasks are stored in `task.json` at the project root. The file is created automatically on first run. Each task entry looks like this:

```json
{
    "id": 1,
    "description": "Buy groceries",
    "completed": false,
    "completed_at": null
}
```

Completed tasks include an ISO 8601 timestamp for `completed_at`, displayed in the table as `DD Mon YYYY, HH:MM`.

---

## Dependencies

| Package       | Purpose                          |
|---------------|----------------------------------|
| `pydantic`    | Task data model and validation   |
| `rich`        | Formatted terminal table output  |
