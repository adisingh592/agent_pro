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
                    role TEXT DEFAULT 'user',
                    content TEXT NOT NULL,
                    model TEXT DEFAULT '',
                    conversation_id TEXT DEFAULT 'default',
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Ensure columns exist if table was created in Phase 1
            cursor.execute("PRAGMA table_info(messages)")
            columns = [row["name"] for row in cursor.fetchall()]
            if "role" not in columns:
                cursor.execute("ALTER TABLE messages ADD COLUMN role TEXT DEFAULT 'user'")
            if "model" not in columns:
                cursor.execute("ALTER TABLE messages ADD COLUMN model TEXT DEFAULT ''")
            if "conversation_id" not in columns:
                cursor.execute("ALTER TABLE messages ADD COLUMN conversation_id TEXT DEFAULT 'default'")

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

            # Tool executions table (Phase 2.2.1)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tool_executions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT DEFAULT 'default',
                    tool_name TEXT NOT NULL,
                    arguments TEXT,
                    result TEXT,
                    status TEXT NOT NULL,
                    duration_ms REAL DEFAULT 0.0,
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

    def save_message(self, role: str, content: str, model: str = "", conversation_id: str = "default") -> int:
        """Save a user or assistant message to database."""
        sender = "You" if role.lower() == "user" else "Agent"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO messages (sender, role, content, model, conversation_id) VALUES (?, ?, ?, ?, ?)",
                (sender, role, content, model, conversation_id)
            )
            conn.commit()
            return cursor.lastrowid

    def get_messages(self, conversation_id: str = "default", limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve historical chat messages."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM (SELECT * FROM messages WHERE conversation_id = ? ORDER BY id DESC LIMIT ?) ORDER BY id ASC",
                (conversation_id, limit)
            )
            return [dict(row) for row in cursor.fetchall()]

    def clear_messages(self, conversation_id: str = "default") -> None:
        """Clear messages for a given conversation."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM messages WHERE conversation_id = ?", (conversation_id,))
            conn.commit()

    def save_tool_execution(
        self,
        tool_name: str,
        arguments: Any,
        result: Any,
        status: str,
        duration_ms: float = 0.0,
        conversation_id: str = "default"
    ) -> int:
        """Save a tool execution record for auditing and conversation history."""
        import json
        args_str = json.dumps(arguments) if not isinstance(arguments, str) else arguments
        res_str = json.dumps(result) if not isinstance(result, str) else result
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO tool_executions (conversation_id, tool_name, arguments, result, status, duration_ms)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (conversation_id, tool_name, args_str, res_str, status, duration_ms))
            conn.commit()
            return cursor.lastrowid

    def get_tool_executions(self, conversation_id: str = "default", limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieve recent tool executions."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM tool_executions WHERE conversation_id = ? ORDER BY id DESC LIMIT ?",
                (conversation_id, limit)
            )
            return [dict(row) for row in cursor.fetchall()]


# Singleton instance
db_manager = DatabaseManager()
