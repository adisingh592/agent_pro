# Personal Agent — Desktop AI Assistant

A high-performance personal desktop AI assistant built with **Python 3.12+**, **PySide6**, and an **SQLite-ready modular architecture**.

Inspired by VS Code, Antigravity, and modern developer workspaces, Personal Agent provides a centralized, professional command center designed for speed, visual clarity, and future autonomous system capabilities.

---

## 📌 Project Status: Phase 1 (100% Complete & Verified)

> **Current Milestone**: Phase 1 Foundation  
> **Status**: Completed, tested, and visually verified against UI reference designs.

---

## 📋 What Has Been Done Till Now (Phase 1 Summary)

### 1. Technology Stack & Foundation
- [x] **Python 3.12+ (Python 3.13 verified)**: Modern typing, clean modular structure.
- [x] **PySide6 (Qt for Python 6.12.0)**: Native, hardware-accelerated desktop UI (no Electron overhead).
- [x] **SQLite Database Layer**: Auto-initializing schema in `data/agent_database.sqlite` with seed datasets for tasks, chat history, memory facts, and activity logs.
- [x] **Custom QSS Styling (`app/ui/theme.qss`)**:
  - Dark charcoal background (`#131417`)
  - Elevated neutral gray surfaces (`#1c1d22`, `#23252b`)
  - Subtle borders (`#282a30`)
  - Crisp high-contrast white text (`#ffffff`) and muted gray labels (`#8e929b`)
  - Restrained warm amber/orange accent (`#e59840`)
- [x] **Standard Python Logging**: Dual output to stdout and rotating persistent log file (`logs/personal_agent.log`).
- [x] **psutil System Monitoring**: Live CPU and RAM usage tracking.

---

### 2. Persistent Window Layout (Three-Part Framework)

The application implements the layout shown in the project reference images:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ PERSONAL AGENT          🔍 Search tasks, files, or commands              ● Agent ready │ (Top Header)
├──────────────┬──────────────────────────────────────────────────────────┬──────────────┤
│ Home         │                                                          │ AGENT STATUS │
│ Agent Chat   │                                                          │  ● Ready     │
│ Tasks        │                                                          ├──────────────┤
│ Files        │                                                          │ CURRENT TASK │
│ Browser      │                  MAIN WORKSPACE                          │  Waiting...  │
│ Coding       │              (11 Modular Page Views)                     ├──────────────┤
│ Workflows    │                                                          │ EXEC. STATE  │
│ Voice        │                                                          │  State: Idle │
│ Memory       │                                                          ├──────────────┤
│ History      │                                                          │ MODEL CONN.  │
│ Settings     │                                                          │  Local Qwen  │
│              │                                                          ├──────────────┤
│              │                                                          │ RECENT ACT.  │
│              │                                                          │  • Init...   │
├──────────────┴──────────────────────────────────────────────────────────┴──────────────┤
│ ● Agent Ready        Local model: not connected          CPU: 2.1% | RAM: 14.8% | Active│ (Status Bar)
└────────────────────────────────────────────────────────────────────────────────────────┘
```

- **Top Header Bar**:
  - Left: Brand title `PERSONAL AGENT` in bold uppercase
  - Center: Global search box (`🔍 Search tasks, files, or commands`) connected to input dispatcher
  - Right: Agent readiness status indicator (`● Agent ready`)
- **Left Sidebar**:
  - 11 navigation destinations with dark card pill backgrounds and warm amber active text.
  - Zero crashes when navigating between views.
- **Center Workspace**:
  - Dynamic `QStackedWidget` hosting all 11 workspace views with smooth transitions.
- **Right Agent Panel (Persistent)**:
  - **AGENT STATUS**: Live status indicator (`● Ready` / `Working`)
  - **CURRENT TASK**: Real-time task title and detail
  - **EXECUTION STATE**: Current state (`Idle`, `Executing`, `Waiting`) with progress bar
  - **MODEL CONNECTION**: Provider and model status (`Local (Ollama): Qwen 2.5 7B`)
  - **RECENT ACTIVITY**: Live bullet log of recent application and agent events
- **Bottom Status Bar**:
  - Agent status dot
  - Active model status (`Local model: not connected`)
  - Real-time CPU and RAM resource metrics updated on a live timer

---

### 3. Detailed Page Implementations

| # | Page | Implemented Capabilities & UI Components | Status |
|---|------|------------------------------------------|--------|
| **1** | **Home** | • Welcome header and workspace subtitle<br>• Command prompt card (*"What would you like me to do?"*) with Enter-key submission<br>• 4 Quick Actions (*Automate task*, *Open application*, *Manage files*, *Start coding*) with direct page routing<br>• Active Tasks overview card dynamically tied to agent execution | ✅ Complete & Interactive |
| **2** | **Agent Chat** | • Natural language conversation UI<br>• Styled message bubbles: amber `"You"` label & card-based `"Agent"` bubble<br>• Pre-seeded dialogue matching `02_agent_chat.png`<br>• Interactive text input with Enter key & Send button (➤)<br>• Attachment (📎) and Mic (🎤) button placeholders<br>• AI Model selector dropdown<br>• Contextual simulated AI responses + auto-scroll | ✅ Complete & Interactive |
| **3** | **Tasks** | • Metric counter card (*Running 0, Waiting 3, Scheduled 0, Completed 0*) bound to database<br>• SQLite-persisted task queue table matching `03_task_manager.png`<br>• Task rows with name, status badge, progress bar, and start time<br>• Interactive **Details** modal and **Stop** button<br>• **＋ Add Task** creation dialog with category selection | ✅ Complete & Interactive |
| **4** | **Files** | • Safe, read-only Windows drive selector (`C:\`, `D:\`, `H:\`)<br>• Directory traversal with Up (↑), Refresh (↻), and breadcrumb path edit<br>• Live file table with Name, Type, Size, and Date Modified<br>• Double-click folder navigation<br>• Real-time filename search filter | ✅ Complete & Functional |
| **5** | **Browser** | • Browser navigation bar with Back (◀), Forward (▶), Reload (↻), and URL input<br>• Agent Browser Controls toolbar (*Take Screenshot*, *Extract Text*, *Inspect Elements*, *Agent Autopilot*)<br>• Dark viewport canvas with session state indicators<br>• Staged for Playwright/CDP automation in Phase 2 | ✅ Complete (UI Pre-wired) |
| **6** | **Coding Workspace** | • VS Code-inspired layout matching `04_coding_workspace.png`<br>• Project Explorer tree (`src/`, `main.py`, `agent.py`, `tools/`, `tests/`, `README.md`)<br>• Code editor preview with `main.py` tab and monospace styling<br>• Bottom Terminal panel with simulated prompt (`> python main.py`) and amber output (`Personal Agent ready`) | ✅ Complete (IDE Staged) |
| **7** | **Workflows** | • Automation Builder matching `05_workflow_builder.png`<br>• Interactive custom canvas rendering connected nodes with warm amber connecting lines:<br>&nbsp;&nbsp;`[ Trigger ] ──── [ Wait for download ] ──── [ Move files ] ──── [ Verify ]`<br>• Toolbar buttons (*＋ Add Trigger*, *＋ Add Action*, *＋ Add Condition*, *💾 Save Workflow*, *▶ Run Workflow*) | ✅ Complete & Interactive |
| **8** | **Voice Assistant** | • Microphone status indicator (*Microphone: Standby / Active*)<br>• Visual audio waveform visualizer widget<br>• Push-to-talk toggle (*🎙 Start Listening* / *⏹ Stop Listening*)<br>• Audio device dropdown and speech engine selector (Whisper Local / Cloud) | ✅ Complete (UI Staged) |
| **9** | **Memory** | • Categorized knowledge base (*Personal preferences*, *Projects*, *Work*, *Applications*, *Frequently used folders*, *Automation preferences*)<br>• Real-time search filter across title and body content<br>• SQLite persistence with live refresh<br>• **＋ Add Memory** dialog to save persistent memory facts | ✅ Complete & Interactive |
| **10** | **History** | • Activity timeline tracking tasks, chat queries, file indexing, and automation events<br>• Category dropdown filter (*All*, *Tasks*, *Chat*, *File Operations*, *Automation*)<br>• Text search box and *Clear History* button | ✅ Complete & Interactive |
| **11** | **Settings** | • 8 tabbed configuration sections: *General*, *Appearance*, *AI Models*, *Local Models*, *API Providers*, *Voice*, *Automation*, *Permissions*<br>• Interactive controls: checkboxes, model dropdowns, password inputs (API keys), sliders, and *Save Changes* confirmation | ✅ Complete & Interactive |

---

### 4. Functional vs. Staged Separation (Phase 1 vs. Future Phases)

To ensure technical transparency, here is the exact operational status of each capability:

| Capability | Phase 1 Status | Future Target |
|---|---|---|
| **GUI Navigation & Layout** | **Fully Functional**: Seamless navigation across all 11 pages, responsive resizing, high-DPI scaling. | Continuous refinement |
| **Chat Interaction** | **Fully Functional**: User messages render, trigger AgentCore processing, log to the right panel, and generate contextual responses. | Streaming AI API integration (Ollama / Gemini / Anthropic) |
| **Task Queue & DB** | **Fully Functional**: SQLite-backed CRUD, task counts, queue display, add/stop tasks. | Background task execution workers & Celery/Queue runner |
| **File Browser** | **Fully Functional**: Real directory indexing, drive selection, path navigation, file filtering (Safe read-only). | File move/copy/rename, automated downloads sorter |
| **Workflow Canvas** | **Fully Functional**: Custom QPainter canvas rendering connected blocks with amber wires. | Drag-and-drop node graph with live automation engine |
| **Browser Engine** | **UI Layout Complete**: Address bar, controls, and viewport placeholder ready. | Playwright / Chromium headless browser integration |
| **Coding Editor** | **UI Layout Complete**: Tree explorer, editor pane, and terminal ready. | Monaco Editor / QScintilla with syntax highlighting and live terminal |
| **Voice Assistant** | **UI Layout Complete**: Push-to-talk state toggle, settings, visualizer ready. | Whisper speech-to-text & Piper/Edge-TTS voice synthesis |
| **Personal Memory** | **Fully Functional**: SQLite memory items categorized, searched, and added dynamically. | Vector embeddings & RAG retrieval |

---

## 🧪 Testing & Verification Results

An automated end-to-end verification suite was built and executed in `tests/test_app.py`:

```
==========================================
 ALL PHASE 1 VERIFICATION TESTS PASSED! 
==========================================
[1/6] Initializing QApplication...                 --> PASSED
[2/6] Instantiating MainWindow...                  --> PASSED
[3/6] Verifying all 11 pages navigate correctly...  --> PASSED (11/11 views)
[4/6] Testing Chat interaction & AgentCore...      --> PASSED (User + Agent signals)
[5/6] Testing SQLite Persistence (Tasks & Memory)...--> PASSED (CRUD + Query)
[6/6] Testing Window Resizing (1024x768 to 1080p)..--> PASSED (No layout breakage)
```

### Visual Verification
Test screenshots rendered during test execution are saved in `tests/screenshots/` and match the reference images:
- `tests/screenshots/test_home.png` matches `ui images/01_home_dashboard.png`
- `tests/screenshots/test_agent_chat.png` matches `ui images/02_agent_chat.png`
- `tests/screenshots/test_tasks.png` matches `ui images/03_task_manager.png`
- `tests/screenshots/test_coding_workspace.png` matches `ui images/04_coding_workspace.png`
- `tests/screenshots/test_workflows.png` matches `ui images/05_workflow_builder.png`

---

## 🛠️ Project File Structure

```
PersonalAgent/
│
├── main.py                     # Application entry point with logging & high-DPI
├── requirements.txt             # PySide6 & psutil dependencies
│
├── app/
│   ├── ui/
│   │   ├── main_window.py       # Assembles Top Bar, Sidebar, Workspace, Agent Panel, Status Bar
│   │   ├── sidebar.py           # Left navigation bar with amber pill selection
│   │   ├── theme.qss            # Custom dark charcoal QSS stylesheet
│   │   │
│   │   ├── pages/               # 11 Modular workspace views
│   │   │   ├── __init__.py
│   │   │   ├── home_page.py
│   │   │   ├── chat_page.py
│   │   │   ├── tasks_page.py
│   │   │   ├── files_page.py
│   │   │   ├── browser_page.py
│   │   │   ├── coding_page.py
│   │   │   ├── workflows_page.py
│   │   │   ├── voice_page.py
│   │   │   ├── memory_page.py
│   │   │   ├── history_page.py
│   │   │   └── settings_page.py
│   │   │
│   │   └── panels/
│   │       ├── __init__.py
│   │       └── agent_panel.py   # Persistent right-side agent monitoring panel
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── agent.py             # Agent state coordinator & response dispatcher
│   │   ├── model_manager.py     # Model provider registry (Local & Cloud)
│   │   ├── task_manager.py      # SQLite task queue manager
│   │   └── system_monitor.py    # psutil CPU/RAM resource monitor
│   │
│   ├── tools/                   # Staged for Phase 2 tool execution
│   │   └── __init__.py
│   ├── automation/              # Staged for Phase 2 task automation
│   │   └── __init__.py
│   ├── memory/
│   │   ├── __init__.py
│   │   └── memory_store.py      # SQLite memory querying and categorization
│   └── database/
│       ├── __init__.py
│       └── db.py                # SQLite schema and default data seed
│
├── data/                        # Persistent SQLite database (`agent_database.sqlite`)
├── logs/                        # Standard logging output (`personal_agent.log`)
├── tests/                       # Automated UI verification suite
│   ├── test_app.py
│   └── screenshots/             # Rendered test screenshots matching UI reference
├── ui images/                   # Provided UI reference screenshots
└── README.md                    # Project documentation & progress report
```

---

## 🚀 How to Run the Application

### 1. Ensure Dependencies Are Installed
```bash
pip install -r requirements.txt
```

### 2. Run Application
```bash
python main.py
```

### 3. Run Automated Tests
```bash
python tests/test_app.py
```

---

## 🔮 Future Roadmap (Beyond Phase 1)

- **Phase 2: Local AI & Tool Execution**
  - Connect Ollama and LM Studio via local streaming APIs.
  - Integrate Playwright for automated browser navigation and form interaction.
  - Implement real file management operations (safe copies, downloads organizer, checksum validation).
- **Phase 3: Coding IDE & Automation Engine**
  - Integrate Monaco Editor / QScintilla for full syntax highlighting and code auto-complete.
  - Execute automated multi-step workflows created in the Automation Builder.
  - Embed local interactive terminal shell (PowerShell / WSL).
- **Phase 4: Multimodal Voice & Autonomous Agents**
  - Local Whisper speech-to-text and Piper/Edge-TTS voice synthesis.
  - Autonomous multi-agent coordination with persistent episodic memory.
