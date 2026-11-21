"""
Memory Page - Personal context, preferences, and long-term memory store.
"""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QScrollArea, QListWidget, QListWidgetItem,
    QDialog, QTextEdit, QMessageBox, QSizePolicy
)
from ...memory.memory_store import MemoryStore


class MemoryCardWidget(QFrame):
    """Card representing a memory item."""

    def __init__(self, title: str, content: str, updated_at: str):
        super().__init__()
        self.setProperty("class", "surfaceCard")
        self.setStyleSheet("""
            MemoryCardWidget {
                background-color: #1c1d22;
                border: 1px solid #282a30;
                border-radius: 8px;
                padding: 14px;
            }
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)

        t_lbl = QLabel(title)
        t_lbl.setStyleSheet("color: #ffffff; font-size: 14px; font-weight: 600;")
        
        c_lbl = QLabel(content)
        c_lbl.setWordWrap(True)
        c_lbl.setStyleSheet("color: #d1d5db; font-size: 13px; line-height: 1.4;")
        
        u_lbl = QLabel(f"Updated: {updated_at}")
        u_lbl.setStyleSheet("color: #8e929b; font-size: 11px;")

        layout.addWidget(t_lbl)
        layout.addWidget(c_lbl)
        layout.addWidget(u_lbl)


class MemoryPage(QWidget):
    """Personal Memory interface with categories and SQLite items."""

    def __init__(self, memory_store: MemoryStore):
        super().__init__()
        self.memory_store = memory_store
        self._current_category = "Personal preferences"
        self._init_ui()
        self.load_category_items(self._current_category)

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(16)

        # Header
        header_layout = QHBoxLayout()
        header_text = QVBoxLayout()
        header_text.setSpacing(4)
        
        title_label = QLabel("Personal Memory")
        title_label.setProperty("class", "pageTitle")
        
        subtitle_label = QLabel("Persistent knowledge, context, user preferences and habits.")
        subtitle_label.setProperty("class", "pageSubtitle")
        
        header_text.addWidget(title_label)
        header_text.addWidget(subtitle_label)
        header_layout.addLayout(header_text, 1)

        add_mem_btn = QPushButton("＋ Add Memory")
        add_mem_btn.setProperty("class", "primaryButton")
        add_mem_btn.setCursor(Qt.PointingHandCursor)
        add_mem_btn.clicked.connect(self._open_add_dialog)
        header_layout.addWidget(add_mem_btn)

        layout.addLayout(header_layout)

        # Category Buttons Bar
        cat_bar = QHBoxLayout()
        cat_bar.setSpacing(8)

        self.cat_buttons = []
        for cat in self.memory_store.get_categories():
            btn = QPushButton(cat)
            btn.setProperty("class", "secondaryButton")
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked=False, c=cat: self._on_category_clicked(c))
            cat_bar.addWidget(btn)
            self.cat_buttons.append((cat, btn))

        cat_bar.addStretch()
        layout.addLayout(cat_bar)

        # Search Bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search memory entries...")
        self.search_input.textChanged.connect(self._on_search)
        layout.addWidget(self.search_input)

        # Items Scroll Area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("background: transparent; border: none;")

        self.cards_container = QWidget()
        self.cards_container.setStyleSheet("background: transparent;")
        self.cards_layout = QVBoxLayout(self.cards_container)
        self.cards_layout.setContentsMargins(0, 0, 0, 0)
        self.cards_layout.setSpacing(12)
        self.cards_layout.addStretch()

        self.scroll_area.setWidget(self.cards_container)
        layout.addWidget(self.scroll_area, 1)

    def _on_category_clicked(self, category: str) -> None:
        self._current_category = category
        self.load_category_items(category)

    def load_category_items(self, category: str) -> None:
        while self.cards_layout.count() > 1:
            item = self.cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        items = self.memory_store.get_items_by_category(category)
        if not items:
            empty_lbl = QLabel(f"No memory entries in '{category}'.")
            empty_lbl.setStyleSheet("color: #8e929b; font-size: 13px; padding: 16px;")
            self.cards_layout.insertWidget(0, empty_lbl)
            return

        for data in items:
            card = MemoryCardWidget(
                title=data.get("title", ""),
                content=data.get("content", ""),
                updated_at=data.get("updated_at", "")
            )
            idx = max(0, self.cards_layout.count() - 1)
            self.cards_layout.insertWidget(idx, card)

    def _on_search(self, text: str) -> None:
        query = text.strip()
        if not query:
            self.load_category_items(self._current_category)
            return

        while self.cards_layout.count() > 1:
            item = self.cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        items = self.memory_store.search_memory(query)
        for data in items:
            card = MemoryCardWidget(
                title=f"[{data.get('category')}] {data.get('title')}",
                content=data.get("content", ""),
                updated_at=data.get("updated_at", "")
            )
            idx = max(0, self.cards_layout.count() - 1)
            self.cards_layout.insertWidget(idx, card)

    def _open_add_dialog(self) -> None:
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Memory Entry")
        dialog.setFixedSize(400, 300)
        dialog.setStyleSheet("background-color: #1c1d22; color: #ffffff;")

        dlg_layout = QVBoxLayout(dialog)
        dlg_layout.setSpacing(10)

        dlg_layout.addWidget(QLabel("Title:"))
        t_input = QLineEdit()
        dlg_layout.addWidget(t_input)

        dlg_layout.addWidget(QLabel("Content / Fact:"))
        c_input = QTextEdit()
        dlg_layout.addWidget(c_input)

        btn_box = QHBoxLayout()
        add_btn = QPushButton("Save")
        add_btn.setProperty("class", "primaryButton")
        add_btn.clicked.connect(lambda: self._save_memory(t_input.text(), c_input.toPlainText(), dialog))
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setProperty("class", "secondaryButton")
        cancel_btn.clicked.connect(dialog.reject)

        btn_box.addStretch()
        btn_box.addWidget(cancel_btn)
        btn_box.addWidget(add_btn)
        dlg_layout.addLayout(btn_box)

        dialog.exec()

    def _save_memory(self, title: str, content: str, dialog: QDialog) -> None:
        if title.strip() and content.strip():
            self.memory_store.add_item(self._current_category, title.strip(), content.strip())
            dialog.accept()
            self.load_category_items(self._current_category)
