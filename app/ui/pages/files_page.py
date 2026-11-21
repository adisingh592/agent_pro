"""
Files Page - File manager for browsing local drives and workspace files.
Safe read-only operations for Phase 1.
"""
import os
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QFrame, QMessageBox, QSizePolicy
)


class FilesPage(QWidget):
    """File manager layout with drive selection, directory traversal, and search."""

    def __init__(self, initial_path: Optional[str] = None):
        super().__init__()
        self.current_path = Path(initial_path or Path.cwd()).resolve()
        self._init_ui()
        self.load_directory(self.current_path)

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(16)

        # Header
        header_layout = QVBoxLayout()
        header_layout.setSpacing(4)
        
        title_label = QLabel("Files")
        title_label.setProperty("class", "pageTitle")
        
        subtitle_label = QLabel("Browse local drives, organize workspace files and monitor downloads.")
        subtitle_label.setProperty("class", "pageSubtitle")
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        layout.addLayout(header_layout)

        # Drive selector bar
        drive_bar = QHBoxLayout()
        drive_bar.setSpacing(8)
        
        drive_lbl = QLabel("Drives:")
        drive_lbl.setStyleSheet("color: #8e929b; font-size: 12px; font-weight: 600;")
        drive_bar.addWidget(drive_lbl)

        # Detect drives on Windows
        drives = self._get_windows_drives()
        for drive in drives:
            d_btn = QPushButton(drive)
            d_btn.setProperty("class", "secondaryButton")
            d_btn.setFixedWidth(50)
            d_btn.setCursor(Qt.PointingHandCursor)
            d_btn.clicked.connect(lambda checked=False, d=drive: self.load_directory(Path(d)))
            drive_bar.addWidget(d_btn)

        drive_bar.addStretch()
        layout.addLayout(drive_bar)

        # Navigation Bar (Up, Path line edit, Refresh, Search)
        nav_bar = QHBoxLayout()
        nav_bar.setSpacing(10)

        up_btn = QPushButton("↑ Up")
        up_btn.setProperty("class", "secondaryButton")
        up_btn.setCursor(Qt.PointingHandCursor)
        up_btn.clicked.connect(self._go_up)
        nav_bar.addWidget(up_btn)

        self.path_edit = QLineEdit(str(self.current_path))
        self.path_edit.returnPressed.connect(self._on_path_entered)
        nav_bar.addWidget(self.path_edit, 1)

        refresh_btn = QPushButton("↻ Refresh")
        refresh_btn.setProperty("class", "secondaryButton")
        refresh_btn.setCursor(Qt.PointingHandCursor)
        refresh_btn.clicked.connect(lambda: self.load_directory(self.current_path))
        nav_bar.addWidget(refresh_btn)

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Filter files...")
        self.search_edit.setFixedWidth(200)
        self.search_edit.textChanged.connect(self._filter_table)
        nav_bar.addWidget(self.search_edit)

        layout.addLayout(nav_bar)

        # Files Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Name", "Type", "Size", "Date Modified"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.itemDoubleClicked.connect(self._on_item_double_clicked)
        layout.addWidget(self.table, 1)

    def _get_windows_drives(self) -> list[str]:
        drives = []
        if sys.platform == "win32":
            import string
            for letter in string.ascii_uppercase:
                drive_str = f"{letter}:\\"
                if os.path.exists(drive_str):
                    drives.append(drive_str)
        return drives or ["C:\\"]

    def load_directory(self, target_path: Path) -> None:
        try:
            target_path = target_path.resolve()
            if not target_path.is_dir():
                return
            self.current_path = target_path
            self.path_edit.setText(str(self.current_path))

            entries = list(os.scandir(str(self.current_path)))
            # Sort: folders first, then files alphabetically
            entries.sort(key=lambda e: (not e.is_dir(), e.name.lower()))

            self.table.setRowCount(len(entries))
            for row, entry in enumerate(entries):
                is_dir = entry.is_dir()
                try:
                    stat = entry.stat()
                    mod_time = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
                    size_str = self._format_size(stat.st_size) if not is_dir else "--"
                except Exception:
                    mod_time = "--"
                    size_str = "--"

                name_item = QTableWidgetItem(f"📁 {entry.name}" if is_dir else f"📄 {entry.name}")
                name_item.setData(Qt.UserRole, entry.path)
                name_item.setData(Qt.UserRole + 1, is_dir)

                type_item = QTableWidgetItem("Folder" if is_dir else Path(entry.name).suffix or "File")
                size_item = QTableWidgetItem(size_str)
                date_item = QTableWidgetItem(mod_time)

                self.table.setItem(row, 0, name_item)
                self.table.setItem(row, 1, type_item)
                self.table.setItem(row, 2, size_item)
                self.table.setItem(row, 3, date_item)

        except PermissionError:
            QMessageBox.warning(self, "Permission Denied", f"Access to {target_path} is denied.")
        except Exception as err:
            QMessageBox.warning(self, "Error", f"Failed to read directory: {err}")

    def _format_size(self, size_bytes: int) -> str:
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"

    def _go_up(self) -> None:
        parent = self.current_path.parent
        if parent and parent != self.current_path:
            self.load_directory(parent)

    def _on_path_entered(self) -> None:
        p = Path(self.path_edit.text().strip())
        if p.exists() and p.is_dir():
            self.load_directory(p)
        else:
            self.path_edit.setText(str(self.current_path))

    def _on_item_double_clicked(self, item: QTableWidgetItem) -> None:
        row = item.row()
        name_item = self.table.item(row, 0)
        if name_item:
            full_path = name_item.data(Qt.UserRole)
            is_dir = name_item.data(Qt.UserRole + 1)
            if is_dir:
                self.load_directory(Path(full_path))
            else:
                QMessageBox.information(self, "File Selected", f"File: {full_path}\n(Read-only in Phase 1)")

    def _filter_table(self, query: str) -> None:
        query = query.strip().lower()
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            show = query in item.text().lower() if item else True
            self.table.setRowHidden(row, not show)
