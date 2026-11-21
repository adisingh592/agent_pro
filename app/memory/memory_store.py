"""
Memory store for personal preferences, work, and agent context.
"""
from typing import List, Dict, Any
from ..database.db import db_manager


class MemoryStore:
    """Manages categorization and querying of persistent memory items."""

    def __init__(self):
        pass

    def get_categories(self) -> List[str]:
        return [
            "Personal preferences",
            "Projects",
            "Work",
            "Applications",
            "Frequently used folders",
            "Automation preferences"
        ]

    def get_items_by_category(self, category: str) -> List[Dict[str, Any]]:
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM memory_items WHERE category = ? ORDER BY id DESC",
                (category,)
            )
            return [dict(row) for row in cursor.fetchall()]

    def search_memory(self, query: str) -> List[Dict[str, Any]]:
        pattern = f"%{query}%"
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM memory_items WHERE title LIKE ? OR content LIKE ? ORDER BY updated_at DESC",
                (pattern, pattern)
            )
            return [dict(row) for row in cursor.fetchall()]

    def add_item(self, category: str, title: str, content: str) -> int:
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO memory_items (category, title, content) VALUES (?, ?, ?)",
                (category, title, content)
            )
            conn.commit()
            return cursor.lastrowid
