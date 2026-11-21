"""
Coding Workspace Page - IDE-like layout inspired by VS Code.
Matches 04_coding_workspace.png reference design.
"""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QTreeWidget, QTreeWidgetItem, QPlainTextEdit, QPushButton,
    QSplitter, QHeaderView, QSizePolicy
)
from PySide6.QtGui import QFont, QColor


class CodingPage(QWidget):
    """IDE layout with Project Explorer, Code Editor, and Terminal panel."""

    def __init__(self):
        super().__init__()
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(16)

        # Header
        header_layout = QVBoxLayout()
        header_layout.setSpacing(4)
        
        title_label = QLabel("Coding Workspace")
        title_label.setProperty("class", "pageTitle")
        
        subtitle_label = QLabel("Project explorer, editor, terminal and agent panel.")
        subtitle_label.setProperty("class", "pageSubtitle")
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        layout.addLayout(header_layout)

        # Main Workspace Container matching 04_coding_workspace.png
        workspace_card = QFrame()
        workspace_card.setProperty("class", "surfaceCard")
        ws_layout = QVBoxLayout(workspace_card)
        ws_layout.setContentsMargins(0, 0, 0, 0)
        ws_layout.setSpacing(0)

        # Horizontal Splitter: Explorer on Left, Editor + Terminal on Right
        h_splitter = QSplitter(Qt.Horizontal)
        h_splitter.setStyleSheet("QSplitter::handle { background-color: #282a30; }")

        # Left Panel: EXPLORER
        explorer_panel = QFrame()
        explorer_panel.setStyleSheet("""
            QFrame {
                background-color: #17181c;
                border-right: 1px solid #282a30;
            }
        """)
        exp_layout = QVBoxLayout(explorer_panel)
        exp_layout.setContentsMargins(12, 14, 12, 14)
        exp_layout.setSpacing(10)

        exp_header = QLabel("EXPLORER")
        exp_header.setStyleSheet("""
            color: #ffffff;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.8px;
        """)
        exp_layout.addWidget(exp_header)

        # Explorer Tree
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setStyleSheet("""
            QTreeWidget {
                background-color: transparent;
                border: none;
                color: #d1d5db;
                font-size: 13px;
            }
            QTreeWidget::item {
                padding: 4px 6px;
            }
            QTreeWidget::item:hover {
                background-color: #202227;
            }
            QTreeWidget::item:selected {
                background-color: #25272e;
                color: #ffffff;
            }
        """)
        self._populate_explorer_tree()
        exp_layout.addWidget(self.tree, 1)

        h_splitter.addWidget(explorer_panel)

        # Right Area: Editor on Top, Terminal on Bottom
        right_panel = QFrame()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        # Editor Area
        editor_container = QFrame()
        editor_layout = QVBoxLayout(editor_container)
        editor_layout.setContentsMargins(16, 12, 16, 12)
        editor_layout.setSpacing(10)

        # Tab Bar
        tab_header = QLabel("main.py")
        tab_header.setStyleSheet("""
            color: #ffffff;
            font-size: 13px;
            font-weight: 700;
            padding: 4px 0px;
        """)
        editor_layout.addWidget(tab_header)

        # Code Editor
        self.editor = QPlainTextEdit()
        font = QFont("Consolas", 11)
        font.setStyleHint(QFont.Monospace)
        self.editor.setFont(font)
        self.editor.setStyleSheet("""
            QPlainTextEdit {
                background-color: #17181c;
                border: none;
                color: #e2e4e9;
                font-family: Consolas, "Courier New", monospace;
                font-size: 13px;
                line-height: 1.6;
            }
        """)
        # Sample code matching reference 04_coding_workspace.png
        self.editor.setPlainText(
            "from pathlib import Path\n\n\n"
            "def main():\n"
            "    print('Personal Agent ready')\n\n\n"
            "if __name__ == '__main__':\n"
            "    main()\n"
        )
        editor_layout.addWidget(self.editor, 1)
        right_layout.addWidget(editor_container, 3)

        # Terminal Panel at Bottom
        terminal_container = QFrame()
        terminal_container.setStyleSheet("""
            QFrame {
                background-color: #141518;
                border-top: 1px solid #282a30;
            }
        """)
        term_layout = QVBoxLayout(terminal_container)
        term_layout.setContentsMargins(16, 12, 16, 12)
        term_layout.setSpacing(6)

        term_title = QLabel("TERMINAL")
        term_title.setStyleSheet("""
            color: #ffffff;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.8px;
        """)
        term_layout.addWidget(term_title)

        term_cmd = QLabel("> python main.py")
        term_cmd.setStyleSheet("color: #d1d5db; font-family: Consolas, monospace; font-size: 13px;")
        term_layout.addWidget(term_cmd)

        term_out = QLabel("Personal Agent ready")
        term_out.setStyleSheet("color: #e59840; font-family: Consolas, monospace; font-size: 13px; font-weight: 600;")
        term_layout.addWidget(term_out)

        right_layout.addWidget(terminal_container, 1)

        h_splitter.addWidget(right_panel)
        h_splitter.setSizes([200, 600])

        ws_layout.addWidget(h_splitter)
        layout.addWidget(workspace_card, 1)

    def _populate_explorer_tree(self) -> None:
        """Populate file tree matching reference image 04_coding_workspace.png."""
        src_item = QTreeWidgetItem(self.tree, ["src/"])
        src_item.setExpanded(True)
        
        main_item = QTreeWidgetItem(src_item, ["main.py"])
        agent_item = QTreeWidgetItem(src_item, ["agent.py"])

        tools_item = QTreeWidgetItem(self.tree, ["tools/"])
        tests_item = QTreeWidgetItem(self.tree, ["tests/"])
        readme_item = QTreeWidgetItem(self.tree, ["README.md"])
