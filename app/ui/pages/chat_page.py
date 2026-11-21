"""
Agent Chat Page - Real-time conversational interface with streaming local AI integration.
Supports progressive token streaming, message persistence, stop generation, and model selection.
"""
from typing import Optional, Dict, Any
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QScrollArea, QComboBox, QMessageBox,
    QSizePolicy
)
from ...core.agent import AgentCore
from ...core.model_manager import ModelManager
from ...database.db import db_manager


class ChatMessageWidget(QFrame):
    """Individual message block for user, agent, or error notifications."""

    def __init__(self, sender: str, text: str = "", is_error: bool = False):
        super().__init__()
        self.sender = sender
        self._text = text
        self.is_error = is_error
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(6)

        if self.is_error:
            self.setStyleSheet("""
                ChatMessageWidget {
                    background-color: #2b1d1f;
                    border: 1px solid #5a272b;
                    border-radius: 8px;
                }
            """)
            author_label = QLabel("System Error")
            author_label.setStyleSheet("color: #ef4444; font-size: 13px; font-weight: 700;")
            self.content_label = QLabel(self._text)
            self.content_label.setWordWrap(True)
            self.content_label.setStyleSheet("color: #fca5a5; font-size: 13px; line-height: 1.4;")
            layout.addWidget(author_label)
            layout.addWidget(self.content_label)

        elif self.sender.lower() == "you":
            self.setStyleSheet("background: transparent; border: none;")
            author_label = QLabel("You")
            author_label.setStyleSheet("color: #e59840; font-size: 13px; font-weight: 700;")
            
            self.content_label = QLabel(self._text)
            self.content_label.setWordWrap(True)
            self.content_label.setStyleSheet("color: #ffffff; font-size: 13px; line-height: 1.4;")
            
            layout.addWidget(author_label)
            layout.addWidget(self.content_label)

        else:
            # Agent Card container matching reference 02_agent_chat.png
            self.setStyleSheet("""
                ChatMessageWidget {
                    background-color: #22242a;
                    border: 1px solid #2c2f38;
                    border-radius: 8px;
                }
            """)
            author_label = QLabel("Agent")
            author_label.setStyleSheet("color: #ffffff; font-size: 13px; font-weight: 700;")
            
            self.content_label = QLabel(self._text)
            self.content_label.setWordWrap(True)
            self.content_label.setStyleSheet("color: #d1d5db; font-size: 13px; line-height: 1.4;")
            
            layout.addWidget(author_label)
            layout.addWidget(self.content_label)

    def append_text(self, new_chunk: str) -> None:
        """Progressively append streamed tokens to the widget."""
        self._text += new_chunk
        self.content_label.setText(self._text)

    def set_text(self, full_text: str) -> None:
        self._text = full_text
        self.content_label.setText(self._text)


class ChatPage(QWidget):
    """Full Chat page with conversation history, live streaming, and model controls."""

    def __init__(self, agent_core: AgentCore, model_manager: ModelManager):
        super().__init__()
        self.agent_core = agent_core
        self.model_manager = model_manager
        self._active_stream_widget: Optional[ChatMessageWidget] = None

        self._init_ui()
        self._load_conversation_history()

        # Connect Agent & Streaming signals
        self.agent_core.message_received.connect(self._on_message_received)
        self.agent_core.stream_started.connect(self._on_stream_started)
        self.agent_core.stream_chunk.connect(self._on_stream_chunk)
        self.agent_core.stream_finished.connect(self._on_stream_finished)
        self.agent_core.stream_error.connect(self._on_stream_error)

        # Connect Model Manager updates
        self.model_manager.models_updated.connect(self._on_models_updated)
        self.model_manager.connection_changed.connect(self._on_connection_changed)

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(16)

        # Header with Title and Clear Chat Button
        header_layout = QHBoxLayout()
        header_text = QVBoxLayout()
        header_text.setSpacing(4)
        
        title_label = QLabel("Agent Chat")
        title_label.setProperty("class", "pageTitle")
        
        subtitle_label = QLabel("Talk naturally. Plan tasks, run tools and follow progress.")
        subtitle_label.setProperty("class", "pageSubtitle")
        
        header_text.addWidget(title_label)
        header_text.addWidget(subtitle_label)
        header_layout.addLayout(header_text, 1)

        # Clear Chat Action
        clear_btn = QPushButton("🗑 Clear Chat")
        clear_btn.setProperty("class", "secondaryButton")
        clear_btn.setToolTip("Clear conversation history")
        clear_btn.setCursor(Qt.PointingHandCursor)
        clear_btn.clicked.connect(self._on_clear_chat)
        header_layout.addWidget(clear_btn)

        layout.addLayout(header_layout)

        # Main Chat Box Card Container
        chat_box = QFrame()
        chat_box.setProperty("class", "surfaceCard")
        chat_box_layout = QVBoxLayout(chat_box)
        chat_box_layout.setContentsMargins(18, 18, 18, 18)
        chat_box_layout.setSpacing(12)

        # Status & Performance Banner
        self.status_banner = QLabel("Ready • Connected to Ollama (" + self.model_manager.active_model + ")")
        self.status_banner.setStyleSheet("color: #8e929b; font-size: 11px; padding-bottom: 4px;")
        chat_box_layout.addWidget(self.status_banner)

        # Scrollable Messages Area
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

        # Text Input Field
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

        # Model Selector Dropdown & Refresh Button
        self.model_combo = QComboBox()
        self.model_combo.setToolTip("Select active local AI model")
        self.model_combo.setStyleSheet("""
            QComboBox {
                background-color: #23252b;
                border: 1px solid #282a30;
                border-radius: 4px;
                color: #ffffff;
                padding: 4px 8px;
                font-size: 11px;
            }
            QComboBox::drop-down {
                border: none;
            }
        """)
        self._populate_models()
        self.model_combo.currentTextChanged.connect(self._on_model_selected)

        refresh_models_btn = QPushButton("↻")
        refresh_models_btn.setToolTip("Refresh installed Ollama models")
        refresh_models_btn.setFixedWidth(24)
        refresh_models_btn.setStyleSheet("background: transparent; border: none; color: #8e929b; font-size: 13px;")
        refresh_models_btn.clicked.connect(self.model_manager.check_connection)

        # Send / Stop Button
        self.action_btn = QPushButton("➤")
        self.action_btn.setToolTip("Send message")
        self.action_btn.setCursor(Qt.PointingHandCursor)
        self.action_btn.setStyleSheet("""
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
        self.action_btn.clicked.connect(self._on_action_clicked)

        input_layout.addWidget(attach_btn)
        input_layout.addWidget(self.input_field, 1)
        input_layout.addWidget(mic_btn)
        input_layout.addWidget(self.model_combo)
        input_layout.addWidget(refresh_models_btn)
        input_layout.addWidget(self.action_btn)

        chat_box_layout.addWidget(input_container)
        layout.addWidget(chat_box, 1)

    def _populate_models(self) -> None:
        self.model_combo.blockSignals(True)
        self.model_combo.clear()
        models = self.model_manager.available_models
        for m in models:
            self.model_combo.addItem(m["name"])

        # Select active
        idx = self.model_combo.findText(self.model_manager.active_model)
        if idx >= 0:
            self.model_combo.setCurrentIndex(idx)
        self.model_combo.blockSignals(False)

    def _on_models_updated(self, model_names: list) -> None:
        self._populate_models()

    def _on_connection_changed(self, display_name: str, is_connected: bool, processor_info: str) -> None:
        if is_connected:
            self.status_banner.setText(f"Connected • {display_name} • {processor_info}")
            self.status_banner.setStyleSheet("color: #8e929b; font-size: 11px;")
        else:
            self.status_banner.setText(f"Disconnected • Ollama offline at {self.model_manager.endpoint}")
            self.status_banner.setStyleSheet("color: #f87171; font-size: 11px;")

    def _load_conversation_history(self) -> None:
        """Load persistent messages from SQLite database."""
        records = db_manager.get_messages(limit=60)
        if records:
            for rec in records:
                sender = rec.get("sender", "You")
                content = rec.get("content", "")
                self._append_message_widget(sender, content)
        else:
            # Seed default conversation matching reference image 02
            self._append_message_widget("You", "Organize my Downloads after all downloads finish.")
            self._append_message_widget(
                "Agent",
                "I'll monitor the folder, wait for active downloads to finish, then organize completed files and verify the destination."
            )

    def _append_message_widget(self, sender: str, text: str, is_error: bool = False) -> ChatMessageWidget:
        widget = ChatMessageWidget(sender, text, is_error=is_error)
        idx = max(0, self.messages_layout.count() - 1)
        self.messages_layout.insertWidget(idx, widget)
        QTimer.singleShot(40, self._scroll_to_bottom)
        return widget

    def _scroll_to_bottom(self) -> None:
        self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        )

    def _on_message_received(self, sender: str, text: str) -> None:
        # If user message, render immediately
        if sender.lower() == "you":
            self._append_message_widget("You", text)

    def _on_stream_started(self, sender: str) -> None:
        self.status_banner.setText(f"Generating response with {self.model_manager.active_model}...")
        self.status_banner.setStyleSheet("color: #e59840; font-size: 11px;")
        self._active_stream_widget = self._append_message_widget("Agent", "")
        
        # Switch action button to Stop (⏹)
        self.action_btn.setText("⏹")
        self.action_btn.setToolTip("Stop generation")
        self.action_btn.setStyleSheet("""
            QPushButton {
                background-color: #ef4444;
                border: none;
                border-radius: 6px;
                color: #ffffff;
                font-size: 13px;
                font-weight: 700;
                padding: 6px 14px;
            }
            QPushButton:hover {
                background-color: #dc2626;
            }
        """)

    def _on_stream_chunk(self, chunk: str) -> None:
        if self._active_stream_widget:
            self._active_stream_widget.append_text(chunk)
            self._scroll_to_bottom()

    def _on_stream_finished(self, full_text: str, stats: dict) -> None:
        self._active_stream_widget = None
        speed = stats.get("tokens_per_sec", 0.0)
        eval_count = stats.get("eval_count", 0)
        self.status_banner.setText(
            f"Ready • Generated {eval_count} tokens ({speed:.1f} tokens/s) on {self.model_manager.active_model}"
        )
        self.status_banner.setStyleSheet("color: #8e929b; font-size: 11px;")
        self._reset_action_button()

    def _on_stream_error(self, err_msg: str) -> None:
        self._active_stream_widget = None
        self._append_message_widget("System", err_msg, is_error=True)
        self.status_banner.setText(f"Inference error: {err_msg[:60]}")
        self.status_banner.setStyleSheet("color: #f87171; font-size: 11px;")
        self._reset_action_button()

    def _reset_action_button(self) -> None:
        self.action_btn.setText("➤")
        self.action_btn.setToolTip("Send message")
        self.action_btn.setStyleSheet("""
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

    def _on_action_clicked(self) -> None:
        if self.agent_core.is_generating:
            self.agent_core.stop_generation()
            self._reset_action_button()
        else:
            self._on_send_clicked()

    def _on_send_clicked(self) -> None:
        text = self.input_field.text().strip()
        if text:
            self.input_field.clear()
            self.agent_core.process_user_input(text)

    def _on_model_selected(self, model_name: str) -> None:
        if model_name:
            self.model_manager.set_active_model(model_name)

    def _on_clear_chat(self) -> None:
        confirm = QMessageBox.question(
            self,
            "Clear Conversation",
            "Are you sure you want to clear the conversation history?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            self.agent_core.clear_conversation()
            while self.messages_layout.count() > 1:
                item = self.messages_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            self.status_banner.setText("Conversation cleared.")
