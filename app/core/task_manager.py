"""
Task Manager for tracking running, waiting, scheduled, completed, and failed tasks.
"""
from typing import List, Dict, Any, Optional
from PySide6.QtCore import QObject, Signal
from ..database.db import db_manager


class TaskManager(QObject):
    """
    Manages task queues, task lifecycles, and SQLite persistence.
    """
    tasks_updated = Signal()
    task_progress = Signal(int, int) # task_id, progress_percentage

    def __init__(self):
        super().__init__()

    def get_all_tasks(self) -> List[Dict[str, Any]]:
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tasks ORDER BY id ASC")
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def get_task_counts(self) -> Dict[str, int]:
        counts = {"running": 0, "waiting": 0, "scheduled": 0, "completed": 0, "failed": 0}
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT status, COUNT(*) as cnt FROM tasks GROUP BY status")
            for row in cursor.fetchall():
                status = row["status"].lower()
                if status in counts:
                    counts[status] = row["cnt"]
        return counts

    def add_task(self, name: str, category: str = "general", status: str = "waiting") -> int:
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO tasks (name, category, status, progress, start_time) VALUES (?, ?, ?, 0, 'Pending')",
                (name, category, status)
            )
            conn.commit()
            task_id = cursor.lastrowid
        self.tasks_updated.emit()
        return task_id

    def update_task_status(self, task_id: int, status: str, progress: int = 0) -> None:
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE tasks SET status = ?, progress = ? WHERE id = ?",
                (status, progress, task_id)
            )
            conn.commit()
        self.tasks_updated.emit()
        self.task_progress.emit(task_id, progress)

    def delete_task(self, task_id: int) -> None:
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            conn.commit()
        self.tasks_updated.emit()
