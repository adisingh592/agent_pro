"""
Database initialization and SQLite manager.
"""
import os
import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "agent_database.sqlite"


class DatabaseManager:
    """Manages SQLite connection and schema for the Personal Agent."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or DB_PATH
        self.init_database()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def init_database(self) -> None:
        """Create tables if they do not exist."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Tasks table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    category TEXT DEFAULT 'general',
                    status TEXT DEFAULT 'waiting',
                    progress INTEGER DEFAULT 0,
                    start_time TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Chat messages table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sender TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Memory table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memory_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Activity log table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS activity_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    description TEXT NOT NULL,
                    status TEXT DEFAULT 'info',
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()

            # Seed default tasks if empty
            cursor.execute("SELECT COUNT(*) FROM tasks")
            if cursor.fetchone()[0] == 0:
                default_tasks = [
                    ("Monitor download folder", "automation", "waiting", 0, "Pending"),
                    ("Open project and run tests", "coding", "waiting", 0, "Pending"),
                    ("Move completed PDFs", "file_ops", "waiting", 0, "Pending"),
                ]
                cursor.executemany(
                    "INSERT INTO tasks (name, category, status, progress, start_time) VALUES (?, ?, ?, ?, ?)",
                    default_tasks
                )
                conn.commit()

            # Seed default memory items if empty
            cursor.execute("SELECT COUNT(*) FROM memory_items")
            if cursor.fetchone()[0] == 0:
                default_memory = [
                    ("Personal preferences", "Default Theme", "Dark charcoal with warm amber accents"),
                    ("Personal preferences", "Notification Sound", "Muted subtle chime"),
                    ("Projects", "Personal AI Agent", "Desktop application built with PySide6 and Python 3.12+"),
                    ("Work", "Primary Workspace", "H:\\pro agent"),
                    ("Applications", "Preferred IDE", "VS Code & Antigravity"),
                    ("Frequently used folders", "Downloads Directory", "C:\\Users\\Downloads"),
                    ("Automation preferences", "Auto-sort PDFs", "Move completed downloads to Documents/PDFs"),
                ]
                cursor.executemany(
                    "INSERT INTO memory_items (category, title, content) VALUES (?, ?, ?)",
                    default_memory
                )
                conn.commit()


# Singleton instance
db_manager = DatabaseManager()
