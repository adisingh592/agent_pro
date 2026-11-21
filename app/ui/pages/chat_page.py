"""
Agent Chat Page - Real-time conversational interface with streaming local AI integration.
Supports progressive token streaming, message persistence, stop generation, and model selection.
"""
from typing import Optional, Dict, Any
from PySide6.QtCore import Qt, QTimer, Signal
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


class ToolActivityWidget(QFrame):
    """
    Visual indicator card for tool invocation matching the professional
    dark charcoal & amber desktop styling.
    """

    def __init__(self, tool_name: str, arguments: Optional[Dict[str, Any]] = None):
        super().__init__()
        self.tool_name = tool_name
        self.arguments = arguments or {}
        self._init_ui()

    def _init_ui(self) -> None:
        self.setStyleSheet("""
            ToolActivityWidget {
                background-color: #1c1e24;
                border: 1px solid #2a2d36;
                border-left: 3px solid #e59840;
                border-radius: 6px;
            }
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(10)

        self.icon_label = QLabel("⚙")
        self.icon_label.setStyleSheet("color: #e59840; font-size: 13px; font-weight: bold;")
        layout.addWidget(self.icon_label)

        display_name = self.tool_name.replace("_", " ").title()
        self.status_label = QLabel(f"Running tool: {display_name}...")
        self.status_label.setStyleSheet("color: #9ca3af; font-size: 12px; font-family: 'Consolas', monospace;")
        layout.addWidget(self.status_label, 1)

        self.duration_label = QLabel("Executing...")
        self.duration_label.setStyleSheet("color: #6b7280; font-size: 11px;")
        layout.addWidget(self.duration_label)

    def set_completed(self, success: bool, duration_ms: float, error_msg: str = "") -> None:
        display_name = self.tool_name.replace("_", " ").title()
        self.duration_label.setText(f"{duration_ms:.1f} ms")

        if success:
            self.icon_label.setText("✓")
            self.icon_label.setStyleSheet("color: #10b981; font-size: 13px; font-weight: bold;")
            self.status_label.setText(f"Tool: {display_name} — Retrieved successfully")
            self.status_label.setStyleSheet("color: #d1d5db; font-size: 12px; font-family: 'Consolas', monospace;")
            self.setStyleSheet("""
                ToolActivityWidget {
                    background-color: #1c1e24;
                    border: 1px solid #233529;
                    border-left: 3px solid #10b981;
                    border-radius: 6px;
                }
            """)
        else:
            self.icon_label.setText("✗")
            self.icon_label.setStyleSheet("color: #ef4444; font-size: 13px; font-weight: bold;")
            self.status_label.setText(f"Tool: {display_name} — Failed: {error_msg}")
            self.status_label.setStyleSheet("color: #fca5a5; font-size: 12px; font-family: 'Consolas', monospace;")
            self.setStyleSheet("""
                ToolActivityWidget {
                    background-color: #241c1e;
                    border: 1px solid #3d2326;
                    border-left: 3px solid #ef4444;
                    border-radius: 6px;
                }
            """)


class ConfirmationCardWidget(QFrame):
    """
    Interactive confirmation card in chat for file write operations (Copy, Move, Rename, Organize).
    Displays Action, Source, Destination, Risk warnings, with [Approve] and [Reject] actions.
    """
    confirmed = Signal(dict)
    rejected = Signal(dict)

    def __init__(self, data: dict):
        super().__init__()
        self.data = data
        self._init_ui()

    def _init_ui(self) -> None:
        self.setStyleSheet("""
            ConfirmationCardWidget {
                background-color: #1a1c22;
                border: 1px solid #e59840;
                border-radius: 8px;
            }
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(10)

        # Header with Shield/Alert Icon
        header_layout = QHBoxLayout()
        icon_lbl = QLabel("🛡️")
        icon_lbl.setStyleSheet("font-size: 14px;")
        title_lbl = QLabel("File Operation Approval Required")
        title_lbl.setStyleSheet("color: #e59840; font-size: 13px; font-weight: 700;")
        header_layout.addWidget(icon_lbl)
        header_layout.addWidget(title_lbl, 1)
        layout.addLayout(header_layout)

        # Details Grid
        details_layout = QVBoxLayout()
        details_layout.setSpacing(4)

        action_text = self.data.get("action", "File Modification")
        action_lbl = QLabel(f"<b>Action:</b> {action_text}")
        action_lbl.setStyleSheet("color: #ffffff; font-size: 12px;")
        details_layout.addWidget(action_lbl)

        source_text = self.data.get("source", "")
        if source_text and source_text != "None":
            src_lbl = QLabel(f"<b>Source:</b> <code>{source_text}</code>")
            src_lbl.setStyleSheet("color: #d1d5db; font-size: 12px;")
            src_lbl.setWordWrap(True)
            details_layout.addWidget(src_lbl)

        dest_text = self.data.get("destination", "")
        if dest_text:
            dest_lbl = QLabel(f"<b>Destination:</b> <code>{dest_text}</code>")
            dest_lbl.setStyleSheet("color: #d1d5db; font-size: 12px;")
            dest_lbl.setWordWrap(True)
            details_layout.addWidget(dest_lbl)

        risk_text = self.data.get("risk", "")
        if risk_text:
            risk_lbl = QLabel(f"<b>Risk:</b> {risk_text}")
            risk_lbl.setStyleSheet("color: #fca5a5; font-size: 11px;")
            risk_lbl.setWordWrap(True)
            details_layout.addWidget(risk_lbl)

        layout.addLayout(details_layout)

        # Action Buttons
        self.btn_layout = QHBoxLayout()
        self.btn_layout.setSpacing(10)

        self.approve_btn = QPushButton("✓ Approve & Execute")
        self.approve_btn.setCursor(Qt.PointingHandCursor)
        self.approve_btn.setStyleSheet("""
            QPushButton {
                background-color: #e59840;
                border: none;
                border-radius: 4px;
                color: #131417;
                font-weight: 700;
                font-size: 12px;
                padding: 6px 16px;
            }
            QPushButton:hover {
                background-color: #f0a34b;
            }
        """)
        self.approve_btn.clicked.connect(self._on_approve)

        self.reject_btn = QPushButton("✕ Reject")
        self.reject_btn.setCursor(Qt.PointingHandCursor)
        self.reject_btn.setStyleSheet("""
            QPushButton {
                background-color: #2a2d36;
                border: 1px solid #3e434f;
                border-radius: 4px;
                color: #d1d5db;
                font-size: 12px;
                padding: 6px 14px;
            }
            QPushButton:hover {
                background-color: #3e434f;
                color: #ffffff;
            }
        """)
        self.reject_btn.clicked.connect(self._on_reject)

        self.btn_layout.addStretch()
        self.btn_layout.addWidget(self.reject_btn)
        self.btn_layout.addWidget(self.approve_btn)
        layout.addLayout(self.btn_layout)

    def _on_approve(self) -> None:
        self.approve_btn.setEnabled(False)
        self.reject_btn.setEnabled(False)
        self.approve_btn.setText("Executing...")
        self.confirmed.emit(self.data)

    def _on_reject(self) -> None:
        self.approve_btn.setEnabled(False)
        self.reject_btn.setEnabled(False)
        self.setStyleSheet("""
            ConfirmationCardWidget {
                background-color: #1c1e24;
                border: 1px solid #5a272b;
                border-radius: 8px;
            }
        """)
        self.reject_btn.setText("Rejected ✗")
        self.rejected.emit(self.data)

    def set_result(self, success: bool, message: str) -> None:
        while self.btn_layout.count():
            item = self.btn_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        status_lbl = QLabel(f"✓ {message}" if success else f"✗ {message}")
        status_lbl.setStyleSheet(f"color: {'#10b981' if success else '#ef4444'}; font-size: 12px; font-weight: bold;")
        self.btn_layout.addWidget(status_lbl)


class ChatPage(QWidget):
    """Full Chat page with conversation history, live streaming, tool indicators, and model controls."""

    def __init__(self, agent_core: AgentCore, model_manager: ModelManager):
        super().__init__()
        self.agent_core = agent_core
        self.model_manager = model_manager
        self._active_stream_widget: Optional[ChatMessageWidget] = None
        self._active_tool_widgets: Dict[str, ToolActivityWidget] = {}

        self._init_ui()
        self._load_conversation_history()

        # Connect Agent & Streaming signals
        self.agent_core.message_received.connect(self._on_message_received)
        self.agent_core.stream_started.connect(self._on_stream_started)
        self.agent_core.stream_chunk.connect(self._on_stream_chunk)
        self.agent_core.stream_finished.connect(self._on_stream_finished)
        self.agent_core.stream_error.connect(self._on_stream_error)

        # Connect Tool Engine signals (Phase 2.2.1 & 2.2.2)
        self.agent_core.tool_call_started.connect(self._on_tool_started)
        self.agent_core.tool_call_finished.connect(self._on_tool_finished)
        self.agent_core.confirmation_requested.connect(self._on_confirmation_requested)

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
        if self._active_stream_widget is None:
            self._active_stream_widget = self._append_message_widget("Agent", "")
        self._active_stream_widget.append_text(chunk)
        self._scroll_to_bottom()

    def _on_tool_started(self, tool_name: str, arguments: dict) -> None:
        display_name = tool_name.replace("_", " ").title()
        self.status_banner.setText(f"🔧 Using tool: {display_name}...")
        self.status_banner.setStyleSheet("color: #e59840; font-size: 11px;")
        
        tool_widget = ToolActivityWidget(tool_name, arguments)
        idx = max(0, self.messages_layout.count() - 1)
        self.messages_layout.insertWidget(idx, tool_widget)
        self._active_tool_widgets[tool_name] = tool_widget
        self._scroll_to_bottom()

    def _on_tool_finished(self, tool_name: str, result: dict, duration_ms: float, success: bool) -> None:
        display_name = tool_name.replace("_", " ").title()
        tool_widget = self._active_tool_widgets.get(tool_name)
        if tool_widget:
            err = result.get("error", "Failed") if not success else ""
            tool_widget.set_completed(success, duration_ms, err)
        
        if success:
            self.status_banner.setText(f"✓ {display_name} retrieved ({duration_ms:.1f}ms) • Analyzing...")
            self.status_banner.setStyleSheet("color: #10b981; font-size: 11px;")
        elif result.get("requires_confirmation"):
            self.status_banner.setText(f"🛡️ Action staged: Awaiting your approval for {display_name}")
            self.status_banner.setStyleSheet("color: #e59840; font-size: 11px;")
        else:
            self.status_banner.setText(f"✗ {display_name} error • Analyzing...")
            self.status_banner.setStyleSheet("color: #ef4444; font-size: 11px;")
        
        self._scroll_to_bottom()

    def _on_confirmation_requested(self, conf_data: dict) -> None:
        """Display an interactive file approval card in the chat."""
        card = ConfirmationCardWidget(conf_data)
        card.confirmed.connect(self._on_card_confirmed)
        card.rejected.connect(self._on_card_rejected)
        idx = max(0, self.messages_layout.count() - 1)
        self.messages_layout.insertWidget(idx, card)
        self._scroll_to_bottom()

    def _on_card_confirmed(self, conf_data: dict) -> None:
        tool_name = conf_data.get("tool", "")
        args = conf_data.get("arguments", {})
        sender_card = self.sender()
        res = self.agent_core.execute_confirmed_tool(tool_name, args)
        if sender_card and hasattr(sender_card, "set_result"):
            is_success = res.get("success", True)
            status_text = res.get("result", {}).get("status", "Operation completed and verified.") if is_success else res.get("error", "Execution failed")
            sender_card.set_result(is_success, status_text)
        self._scroll_to_bottom()

    def _on_card_rejected(self, conf_data: dict) -> None:
        sender_card = self.sender()
        if sender_card and hasattr(sender_card, "set_result"):
            sender_card.set_result(False, "Operation rejected by user.")
        self.agent_core.log_activity("Operation rejected by user")
        self._scroll_to_bottom()

    def _on_stream_finished(self, full_text: str, stats: dict) -> None:
        self._active_stream_widget = None
        self._active_tool_widgets.clear()
        speed = stats.get("tokens_per_sec", 0.0)
        eval_count = stats.get("eval_count", 0)
        rounds = stats.get("rounds", 1)
        round_info = f" in {rounds} round{'s' if rounds > 1 else ''}" if rounds > 1 else ""
        self.status_banner.setText(
            f"Ready • Generated {eval_count} tokens ({speed:.1f} tokens/s){round_info} on {self.model_manager.active_model}"
        )
        self.status_banner.setStyleSheet("color: #8e929b; font-size: 11px;")
        self._reset_action_button()

    def _on_stream_error(self, err_msg: str) -> None:
        self._active_stream_widget = None
        self._active_tool_widgets.clear()
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
            self._active_stream_widget = None
            self._active_tool_widgets.clear()
            while self.messages_layout.count() > 1:
                item = self.messages_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            self.status_banner.setText("Conversation cleared.")
