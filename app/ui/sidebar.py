"""
Sidebar Navigation - Left-hand persistent navigation list.
Matches reference UI (01_home_dashboard.png to 05_workflow_builder.png).
"""
from typing import List
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QSizePolicy
)


class Sidebar(QFrame):
    """Compact, professional dark sidebar with 11 navigation destinations."""
    page_selected = Signal(str)

    NAV_ITEMS = [
        "Home",
        "Agent Chat",
        "Tasks",
        "Files",
        "Browser",
        "Coding Workspace",
        "Workflows",
        "Voice",
        "Memory",
        "History",
        "Settings"
    ]

    def __init__(self):
        super().__init__()
        self.setObjectName("sidebar")
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 16, 10, 16)
        layout.setSpacing(8)

        # Nav list
        self.list_widget = QListWidget()
        self.list_widget.setObjectName("sidebarList")
        self.list_widget.setFocusPolicy(Qt.NoFocus)

        for name in self.NAV_ITEMS:
            item = QListWidgetItem(name)
            self.list_widget.addItem(item)

        self.list_widget.setCurrentRow(0)
        self.list_widget.currentItemChanged.connect(self._on_item_changed)

        layout.addWidget(self.list_widget, 1)

    def _on_item_changed(self, current: QListWidgetItem, previous: QListWidgetItem) -> None:
        if current:
            self.page_selected.emit(current.text())

    def select_page(self, name: str) -> None:
        for row in range(self.list_widget.count()):
            item = self.list_widget.item(row)
            if item.text().lower() == name.lower():
                self.list_widget.setCurrentRow(row)
                break
