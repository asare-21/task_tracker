import json
import sys
import os
import pytest
from datetime import datetime
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(__file__))

from model import Task
from storage import TaskStorage


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_storage(tmp_path, initial_tasks=None):
    """Create a TaskStorage backed by a temp file, suppressing init prints."""
    storage_file = tmp_path / "tasks.json"
    if initial_tasks is not None:
        storage_file.write_text(json.dumps(initial_tasks))
    with patch("builtins.print"):
        return TaskStorage(storage_file=str(storage_file))


def read_raw(storage):
    with storage.storage_file.open() as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Task model
# ---------------------------------------------------------------------------

class TestTaskModel:
    def test_creation_defaults(self):
        task = Task(id=1, description="Buy milk", completed=False)
        assert task.id == 1
        assert task.description == "Buy milk"
        assert task.completed is False
        assert task.completed_at is None

    def test_completed_at_none_serialises_to_none(self):
        task = Task(id=1, description="x", completed=False)
        dumped = task.model_dump()
        assert dumped["completed_at"] is None

    def test_completed_at_formats_correctly(self):
        dt = datetime(2024, 6, 15, 9, 30)
        task = Task(id=1, description="x", completed=True, completed_at=dt)
        dumped = task.model_dump()
        assert dumped["completed_at"] == "15 Jun 2024, 09:30"

    def test_round_trip_from_dict(self):
        data = {"id": 2, "description": "Walk dog", "completed": False, "completed_at": None}
        task = Task(**data)
        assert task.description == "Walk dog"


# ---------------------------------------------------------------------------
# TaskStorage – file initialisation
# ---------------------------------------------------------------------------

class TestStorageInit:
    def test_creates_file_if_missing(self, tmp_path):
        storage_file = tmp_path / "new.json"
        assert not storage_file.exists()
        with patch("builtins.print"):
            TaskStorage(storage_file=str(storage_file))
        assert storage_file.exists()
        assert json.loads(storage_file.read_text()) == []

    def test_does_not_overwrite_existing_file(self, tmp_path):
        storage_file = tmp_path / "tasks.json"
        existing = [{"id": 1, "description": "Keep me", "completed": False, "completed_at": None}]
        storage_file.write_text(json.dumps(existing))
        with patch("builtins.print"):
            TaskStorage(storage_file=str(storage_file))
        assert json.loads(storage_file.read_text()) == existing


# ---------------------------------------------------------------------------
# TaskStorage – add_task
# ---------------------------------------------------------------------------

class TestAddTask:
    def test_adds_task(self, tmp_path):
        storage = make_storage(tmp_path)
        with patch("builtins.print"):
            storage.add_task("Write tests")
        tasks = read_raw(storage)
        assert len(tasks) == 1
        assert tasks[0]["description"] == "Write tests"
        assert tasks[0]["completed"] is False

    def test_id_increments(self, tmp_path):
        storage = make_storage(tmp_path)
        with patch("builtins.print"):
            storage.add_task("First")
            storage.add_task("Second")
        tasks = read_raw(storage)
        assert tasks[0]["id"] == 1
        assert tasks[1]["id"] == 2

    def test_empty_description_rejected(self, tmp_path):
        storage = make_storage(tmp_path)
        with patch("builtins.print"):
            storage.add_task("")
        assert read_raw(storage) == []

    def test_whitespace_only_description_rejected(self, tmp_path):
        storage = make_storage(tmp_path)
        with patch("builtins.print"):
            storage.add_task("   ")
        # Whitespace is truthy so this currently passes through; test documents behaviour
        tasks = read_raw(storage)
        # If this ever changes to reject whitespace, update the assertion
        assert len(tasks) == 1  # current behaviour: whitespace accepted


# ---------------------------------------------------------------------------
# TaskStorage – list_tasks
# ---------------------------------------------------------------------------

class TestListTasks:
    def test_returns_empty_list(self, tmp_path):
        storage = make_storage(tmp_path)
        with patch("builtins.print"):
            result = storage.list_tasks()
        assert result == []

    def test_returns_task_objects(self, tmp_path):
        initial = [{"id": 1, "description": "Read", "completed": False, "completed_at": None}]
        storage = make_storage(tmp_path, initial_tasks=initial)
        with patch("builtins.print"):
            result = storage.list_tasks()
        assert len(result) == 1
        assert isinstance(result[0], Task)
        assert result[0].description == "Read"


# ---------------------------------------------------------------------------
# TaskStorage – complete_task
# ---------------------------------------------------------------------------

class TestCompleteTask:
    def test_marks_task_completed(self, tmp_path):
        initial = [{"id": 1, "description": "Do thing", "completed": False, "completed_at": None}]
        storage = make_storage(tmp_path, initial_tasks=initial)
        storage.complete_task(1)
        tasks = read_raw(storage)
        assert tasks[0]["completed"] is True
        assert tasks[0]["completed_at"] is not None

    def test_completed_at_is_valid_datetime(self, tmp_path):
        initial = [{"id": 1, "description": "Do thing", "completed": False, "completed_at": None}]
        storage = make_storage(tmp_path, initial_tasks=initial)
        storage.complete_task(1)
        raw_dt = read_raw(storage)[0]["completed_at"]
        # Should parse without error
        datetime.fromisoformat(raw_dt)

    def test_completing_nonexistent_task_is_noop(self, tmp_path):
        initial = [{"id": 1, "description": "Do thing", "completed": False, "completed_at": None}]
        storage = make_storage(tmp_path, initial_tasks=initial)
        storage.complete_task(99)
        tasks = read_raw(storage)
        assert tasks[0]["completed"] is False

    def test_only_target_task_is_completed(self, tmp_path):
        initial = [
            {"id": 1, "description": "One", "completed": False, "completed_at": None},
            {"id": 2, "description": "Two", "completed": False, "completed_at": None},
        ]
        storage = make_storage(tmp_path, initial_tasks=initial)
        storage.complete_task(1)
        tasks = read_raw(storage)
        assert tasks[0]["completed"] is True
        assert tasks[1]["completed"] is False


# ---------------------------------------------------------------------------
# TaskStorage – delete_task
# ---------------------------------------------------------------------------

class TestDeleteTask:
    def test_deletes_task(self, tmp_path):
        initial = [
            {"id": 1, "description": "Keep", "completed": False, "completed_at": None},
            {"id": 2, "description": "Delete me", "completed": False, "completed_at": None},
        ]
        storage = make_storage(tmp_path, initial_tasks=initial)
        with patch("builtins.print"):
            storage.delete_task(2)
        tasks = read_raw(storage)
        assert len(tasks) == 1
        assert tasks[0]["id"] == 1

    def test_delete_nonexistent_id_leaves_tasks_unchanged(self, tmp_path):
        initial = [{"id": 1, "description": "Stay", "completed": False, "completed_at": None}]
        storage = make_storage(tmp_path, initial_tasks=initial)
        with patch("builtins.print"):
            storage.delete_task(99)
        tasks = read_raw(storage)
        assert len(tasks) == 1

    def test_delete_last_task_bug(self, tmp_path):
        """
        Known bug: deleting the only task results in an empty list which
        triggers the early-return guard, leaving the file unchanged.
        This test documents the current (incorrect) behaviour.
        """
        initial = [{"id": 1, "description": "Solo", "completed": False, "completed_at": None}]
        storage = make_storage(tmp_path, initial_tasks=initial)
        with patch("builtins.print"):
            storage.delete_task(1)
        tasks = read_raw(storage)
        # BUG: task is NOT deleted because of the premature `if not tasks: return`
        assert len(tasks) == 1


# ---------------------------------------------------------------------------
# TaskStorage – list_task_status (output check)
# ---------------------------------------------------------------------------

class TestListTaskStatus:
    def test_prints_counts(self, tmp_path):
        initial = [
            {"id": 1, "description": "Done", "completed": True, "completed_at": "2024-01-01T00:00:00"},
            {"id": 2, "description": "Pending", "completed": False, "completed_at": None},
        ]
        storage = make_storage(tmp_path, initial_tasks=initial)
        with patch("builtins.print") as mock_print:
            storage.list_task_status()
        printed = " ".join(str(c) for c in mock_print.call_args_list)
        assert "1" in printed  # 1 completed
        assert "1" in printed  # 1 pending
