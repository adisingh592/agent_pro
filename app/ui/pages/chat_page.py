"""
Agent Chat Page - Primary natural language conversation interface.
Matches 02_agent_chat.png reference design.
"""
from typing import Optional
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QScrollArea, QComboBox, QSizePolicy
)
from ...core.agent import AgentCore
from ...core.model_manager import ModelManager


class ChatMessageWidget(QFrame):
    """Individual message block for user or agent."""

    def __init__(self, sender: str, text: str):
        super().__init__()
        self.sender = sender
        self.text = text
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)

        if self.sender.lower() == "you":
            # User Message
            author_label = QLabel("You")
            author_label.setStyleSheet("color: #e59840; font-size: 13px; font-weight: 700;")
            
            content_label = QLabel(self.text)
            content_label.setWordWrap(True)
            content_label.setStyleSheet("color: #ffffff; font-size: 13px; line-height: 1.4;")
            
            layout.addWidget(author_label)
            layout.addWidget(content_label)
            self.setStyleSheet("background: transparent; border: none;")

        else:
            # Agent Message - Card container matching reference 02_agent_chat.png
            self.setStyleSheet("""
                ChatMessageWidget {
                    background-color: #22242a;
                    border: 1px solid #2c2f38;
                    border-radius: 8px;
                }
            """)
            author_label = QLabel("Agent")
            author_label.setStyleSheet("color: #ffffff; font-size: 13px; font-weight: 700;")
            
            content_label = QLabel(self.text)
            content_label.setWordWrap(True)
            content_label.setStyleSheet("color: #d1d5db; font-size: 13px; line-height: 1.4;")
            
            layout.addWidget(author_label)
            layout.addWidget(content_label)


class ChatPage(QWidget):
    """Full Chat page with conversation history and input controls."""

    def __init__(self, agent_core: AgentCore, model_manager: ModelManager):
        super().__init__()
        self.agent_core = agent_core
        self.model_manager = model_manager
        self._init_ui()
        self._seed_default_conversation()

        # Connect Agent signal
        self.agent_core.message_received.connect(self.add_message)

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(16)

        # Header
        header_layout = QVBoxLayout()
        header_layout.setSpacing(4)
        
        title_label = QLabel("Agent Chat")
        title_label.setProperty("class", "pageTitle")
        
        subtitle_label = QLabel("Talk naturally. Plan tasks, run tools and follow progress.")
        subtitle_label.setProperty("class", "pageSubtitle")
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        layout.addLayout(header_layout)

        # Main Chat Box Container
        chat_box = QFrame()
        chat_box.setProperty("class", "surfaceCard")
        chat_box_layout = QVBoxLayout(chat_box)
        chat_box_layout.setContentsMargins(18, 18, 18, 18)
        chat_box_layout.setSpacing(14)

        # Scrollable messages area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("background: transparent; border: none;")
        
        self.messages_container = QWidget()
        self.messages_container.setStyleSheet("background: transparent;")
        self.messages_layout = QVBoxLayout(self.messages_container)
        self.messages_layout.setContentsMargins(4, 4, 4, 4)
        self.messages_layout.setSpacing(14)
        self.messages_layout.addStretch()

        self.scroll_area.setWidget(self.messages_container)
        chat_box_layout.addWidget(self.scroll_area, 1)

        # Chat Input Container at bottom of the card
        input_container = QFrame()
        input_container.setObjectName("chatInputContainer")
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(10, 6, 10, 6)
        input_layout.setSpacing(10)

        # Attachment Button Placeholder
        attach_btn = QPushButton("📎")
        attach_btn.setToolTip("Attach files (Placeholder)")
        attach_btn.setCursor(Qt.PointingHandCursor)
        attach_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #8e929b;
                font-size: 14px;
                padding: 4px;
            }
            QPushButton:hover {
                color: #e59840;
            }
        """)

        # Text input field
        self.input_field = QLineEdit()
        self.input_field.setObjectName("chatInputField")
        self.input_field.setPlaceholderText("Ask a question or give me a task...")
        self.input_field.returnPressed.connect(self._on_send_clicked)

        # Mic Button Placeholder
        mic_btn = QPushButton("🎤")
        mic_btn.setToolTip("Voice input (Placeholder)")
        mic_btn.setCursor(Qt.PointingHandCursor)
        mic_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #8e929b;
                font-size: 14px;
                padding: 4px;
            }
            QPushButton:hover {
                color: #e59840;
            }
        """)

        # Model Selector Placeholder
        self.model_combo = QComboBox()
        self.model_combo.setToolTip("Select active AI model")
        self.model_combo.setStyleSheet("""
            QComboBox {
                background-color: #23252b;
                border: 1px solid #282a30;
                border-radius: 4px;
                color: #9ca3af;
                padding: 4px 8px;
                font-size: 11px;
            }
            QComboBox::drop-down {
                border: none;
            }
        """)
        for m in self.model_manager.available_models:
            self.model_combo.addItem(f"{m['name']}")

        # Send Button
        send_btn = QPushButton("➤")
        send_btn.setToolTip("Send message")
        send_btn.setCursor(Qt.PointingHandCursor)
        send_btn.setStyleSheet("""
            QPushButton {
                background-color: #e59840;
                border: none;
                border-radius: 6px;
                color: #131417;
                font-size: 13px;
                font-weight: 700;
                padding: 6px 14px;
            }
            QPushButton:hover {
                background-color: #f0a34b;
            }
            QPushButton:pressed {
                background-color: #c98030;
            }
        """)
        send_btn.clicked.connect(self._on_send_clicked)

        input_layout.addWidget(attach_btn)
        input_layout.addWidget(self.input_field, 1)
        input_layout.addWidget(mic_btn)
        input_layout.addWidget(self.model_combo)
        input_layout.addWidget(send_btn)

        chat_box_layout.addWidget(input_container)
        layout.addWidget(chat_box, 1)

    def _seed_default_conversation(self) -> None:
        """Seed initial messages matching reference image 02_agent_chat.png."""
        self.add_message("You", "Organize my Downloads after all downloads finish.")
        self.add_message(
            "Agent",
            "I'll monitor the folder, wait for active downloads to finish, then organize completed files and verify the destination."
        )

    def add_message(self, sender: str, text: str) -> None:
        msg_widget = ChatMessageWidget(sender, text)
        # Insert before stretch item
        idx = max(0, self.messages_layout.count() - 1)
        self.messages_layout.insertWidget(idx, msg_widget)
        
        # Scroll to bottom
        QTimer.singleShot(50, self._scroll_to_bottom)

    def _scroll_to_bottom(self) -> None:
        self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        )

    def _on_send_clicked(self) -> None:
        text = self.input_field.text().strip()
        if text:
            self.input_field.clear()
            self.agent_core.process_user_input(text)
