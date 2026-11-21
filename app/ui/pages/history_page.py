"""
History Page - Comprehensive timeline of tasks, conversations, and automation.
"""
from datetime import datetime
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QComboBox, QLineEdit, QSizePolicy
)
from ...database.db import db_manager


class HistoryItemWidget(QFrame):
    """Timeline entry card."""

    def __init__(self, category: str, description: str, timestamp: str, status: str):
        super().__init__()
        self.setProperty("class", "surfaceCard")
        self.setStyleSheet("""
            HistoryItemWidget {
                background-color: #1c1d22;
                border: 1px solid #282a30;
                border-radius: 6px;
                padding: 10px 14px;
            }
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(14)

        # Category Badge
        cat_badge = QLabel(category.upper())
        cat_badge.setProperty("class", "statusBadge")
        cat_badge.setFixedWidth(90)
        cat_badge.setAlignment(Qt.AlignCenter)
        layout.addWidget(cat_badge)

        # Description
        desc_lbl = QLabel(description)
        desc_lbl.setStyleSheet("color: #ffffff; font-size: 13px;")
        layout.addWidget(desc_lbl, 1)

        # Timestamp
        time_lbl = QLabel(timestamp)
        time_lbl.setStyleSheet("color: #8e929b; font-size: 11px;")
        layout.addWidget(time_lbl)


class HistoryPage(QWidget):
    """Activity History layout with category filters and search."""

    def __init__(self):
        super().__init__()
        self._init_ui()
        self.load_history()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(16)

        # Header
        header_layout = QHBoxLayout()
        header_text = QVBoxLayout()
        header_text.setSpacing(4)
        
        title_label = QLabel("Activity History")
        title_label.setProperty("class", "pageTitle")
        
        subtitle_label = QLabel("Comprehensive log of agent tasks, conversations and automation events.")
        subtitle_label.setProperty("class", "pageSubtitle")
        
        header_text.addWidget(title_label)
        header_text.addWidget(subtitle_label)
        header_layout.addLayout(header_text, 1)

        clear_btn = QPushButton("Clear History")
        clear_btn.setProperty("class", "secondaryButton")
        clear_btn.setCursor(Qt.PointingHandCursor)
        clear_btn.clicked.connect(self._clear_history)
        header_layout.addWidget(clear_btn)

        layout.addLayout(header_layout)

        # Filters Bar
        filter_bar = QHBoxLayout()
        filter_bar.setSpacing(10)

        self.cat_filter = QComboBox()
        self.cat_filter.addItems(["All Categories", "Tasks", "Chat", "File Operations", "Automation"])
        self.cat_filter.currentIndexChanged.connect(self.load_history)
        filter_bar.addWidget(self.cat_filter)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Filter history events...")
        self.search_box.textChanged.connect(self.load_history)
        filter_bar.addWidget(self.search_box, 1)

        layout.addLayout(filter_bar)

        # History Scroll Area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("background: transparent; border: none;")

        self.items_container = QWidget()
        self.items_container.setStyleSheet("background: transparent;")
        self.items_layout = QVBoxLayout(self.items_container)
        self.items_layout.setContentsMargins(0, 0, 0, 0)
        self.items_layout.setSpacing(10)
        self.items_layout.addStretch()

        self.scroll_area.setWidget(self.items_container)
        layout.addWidget(self.scroll_area, 1)

    def load_history(self) -> None:
        while self.items_layout.count() > 1:
            item = self.items_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Seed realistic history items
        sample_events = [
            ("Tasks", "Task created: Monitor download folder", "Today 10:15", "completed"),
            ("Chat", "Prompt: Organize my Downloads after all downloads finish", "Today 10:14", "completed"),
            ("File Operations", "Workspace directory indexed: H:\\pro agent", "Today 10:12", "info"),
            ("Automation", "Initialized background event dispatcher", "Today 10:10", "info"),
            ("System", "Personal Agent Phase 1 desktop engine started", "Today 10:09", "info"),
        ]

        selected_cat = self.cat_filter.currentText()
        query = self.search_box.text().strip().lower()

        for cat, desc, t_stamp, status in sample_events:
            if selected_cat != "All Categories" and cat.lower() != selected_cat.lower():
                continue
            if query and query not in desc.lower() and query not in cat.lower():
                continue

            widget = HistoryItemWidget(cat, desc, t_stamp, status)
            idx = max(0, self.items_layout.count() - 1)
            self.items_layout.insertWidget(idx, widget)

    def _clear_history(self) -> None:
        while self.items_layout.count() > 1:
            item = self.items_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
