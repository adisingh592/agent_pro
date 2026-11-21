# PERSONAL AGENT — COMPREHENSIVE CONTEXT & STATUS BRIEFING FOR GPT / LLMs
**Document:** `GPT_README.md`  
**Purpose:** Universal context transfer document so ChatGPT / GPT / any LLM can instantly understand the complete project state, architecture, completed phases, safety invariants, and upcoming milestones.  
**Generated At:** November 2026  
**Repository:** [https://github.com/adisingh592/agent_pro.git](https://github.com/adisingh592/agent_pro.git) (Branch: `main`)  
**Operating System:** Windows 11 Home / Pro (64-bit)  

---

## 1. Executive Summary & Project Identity

**Personal Agent** is a production-grade Windows desktop application built with **Python 3.12+** and **PySide6 (Qt for Python)**. It is powered by a **locally hosted Large Language Model (Qwen 3 8B via Ollama with NVIDIA GPU acceleration)** and features a modular, safe, multi-round tool execution engine.

The project is currently evolving from a conversational assistant with file and process intelligence into a **unified autonomous computer-use agent** capable of operating desktop software via Windows UI Automation, browser DOM automation, and visual grounding.

### Core Philosophy & Strict Development Rules
1. **Do NOT rebuild or redesign the application:** The existing PySide6 UI, dark charcoal/amber theme, SQLite database, and Ollama integration are fully operational.
2. **Do NOT break previous phase functionality:** All 41 existing automated unit and integration tests must remain at 100% passing.
3. **Hardware-bound execution:** All local intelligence runs strictly on the host's **NVIDIA RTX 3050 Laptop GPU (6GB VRAM)**. Secondary heavy models (e.g. 7B/72B multimodal models) cannot be loaded concurrently in GPU memory.
4. **Safety-first desktop control:** No mutating or destructive action (closing apps, modifying files, executing commands) can ever execute without explicit user approval via interactive UI confirmation cards.

---

## 2. Hardware & Runtime Environment Specifications

| Component | Specification | Operational Configuration |
| :--- | :--- | :--- |
| **Operating System** | Windows 11 (64-bit) | PowerShell / CMD runtime |
| **Processor (CPU)** | Intel Core i7-13650HX (14 cores, 20 threads) | Host execution & multithreading |
| **System Memory (RAM)**| 32 GB DDR5 | Application, caching & background workers |
| **Graphics (GPU)** | NVIDIA GeForce RTX 3050 Laptop GPU (6 GB GDDR6 VRAM) | Hardware-accelerated LLM inference |
| **Local LLM Engine** | Ollama daemon (`http://localhost:11434`) | `llamacpp` CUDA v12 runner |
| **Active Model** | `qwen3:8b` (5.2 GB GGUF, Q4_K_M quantization) | `num_ctx: 4096`, 70% GPU offload, ~4,218 MiB VRAM used |
| **Inference Speed** | **18.3 – 20.4 tokens/second** | Non-blocking streaming via `QThread` |
| **UI Framework** | PySide6 6.7+ (Qt for Python) | Dark charcoal (`#181a1f`) + Warm Amber (`#e59840`) |
| **Database** | SQLite 3 (`data/agent_database.sqlite`) | WAL mode, thread-isolated connections |

---

## 3. Current Phase Completion Matrix (What is 100% Done)

```
[Phase 1]       ████████████████████ 100% Complete (Desktop UI Foundation)
[Phase 2.1]     ████████████████████ 100% Complete (Local AI & GPU Acceleration)
[Phase 2.2.1]   ████████████████████ 100% Complete (Agent Tool Engine)
[Phase 2.2.2]   ████████████████████ 100% Complete (File Intelligence & Safe Ops)
[Phase 2.2.3]   ████████████████████ 100% Complete (App & Process Control)
[Milestone A]   ████████████████████ 100% Complete (Computer Automation Architecture & Safety)
[Milestones B-I]░░░░░░░░░░░░░░░░░░░░   0% Staged (Awaiting User Review to begin Milestone B)
```

### Detailed Breakdown of Completed Phases

#### ✅ Phase 1: Desktop UI Foundation
- Complete 3-part layout: Collapsible left navigation sidebar, center multi-view stack, persistent right agent status panel, and bottom system status bar.
- **11 Fully Functional Dedicated Views:**
  1. `Home`: System dashboard, quick action cards, hardware gauges.
  2. `Agent Chat`: Conversational interface, markdown formatting, tool badges, staged approval cards.
  3. `Tasks`: Task list, priority scheduling, progress tracking.
  4. `Files`: Workspace explorer, file viewer, recent file tracker.
  5. `Browser`: Embedded web view / automation controller tab.
  6. `Coding Workspace`: Monaco/code editor surface and project tree.
  7. `Workflows`: Node-based automation pipeline canvas.
  8. `Voice Assistant`: Speech interface controls.
  9. `Memory`: Long-term agent memory inspection and search.
  10. `History`: Audit logs and past interaction transcripts.
  11. `Settings`: Model configuration, Ollama URL, GPU parameter tuning, theme preferences.

#### ✅ Phase 2.1: Local AI Integration & GPU Acceleration
- `OllamaClient` wrapper handling model discovery, generation, and multi-round chat calls.
- `ModelManager` discovering local models, checking daemon health, and configuring parameters (`temperature: 0.7`, `num_ctx: 4096`).
- Asynchronous non-blocking token streaming via `OllamaChatWorker` (`QThread`), emitting `chunk_received`, `status_changed`, `reasoning_chunk_received`, and `generation_finished` signals.
- Transparent separation of deep reasoning `<think>` tokens from visible conversational responses.
- Instant stop generation mechanism (`⏹` button) cleanly terminating threads.

#### ✅ Phase 2.2.1: Agent Tool Engine
- **5-Stage Execution Pipeline:**
  `Model Decision` ➔ `JSON Schema Validation` ➔ `Permission Policy Check` ➔ `Isolated Execution with Duration Timing` ➔ `Result Analysis by Model`.
- `ToolRegistry`: In-memory metadata catalog storing parameter schemas, descriptions, and permission requirements.
- `ToolValidator`: Validates argument types, mandatory fields, rejects unexpected keys, and provides descriptive error payloads.
- `ToolPermissions`: 3-tier permission model (`AUTOMATIC`, `CONFIRMATION_REQUIRED`, `RESTRICTED`).
- `ToolExecutor`: Manages tool execution, enforces timeouts (15s default), measures execution time in milliseconds, and logs to SQLite.
- Multi-round tool execution loop (up to 5 rounds) allowing the agent to chain multiple tool calls before answering.
- Built-in safe system inspection tools: `get_current_time`, `get_system_info`, `get_gpu_info`.
- `ToolActivityWidget`: Real-time chat widget displaying status, execution timing, and success/failure badges.

#### ✅ Phase 2.2.2: File Intelligence & Safe File Operations
- `FileSecurityManager`: Enforces strict filesystem boundaries.
  - Hard blocks access to `C:\Windows`, `C:\Windows\System32`, `C:\Program Files`, `C:\ProgramData`.
  - Canonical path resolution and path traversal prevention (`..` escape blocking).
- **6 Read-Only Tools (Auto-Approved):**
  - `search_files`: Recursive wildcard search (`*.py`, `*report*`) with 500-result cap.
  - `list_directory`: Folder listing with file/directory classification, sizes, and timestamps.
  - `get_file_info`: Metadata extraction (full path, size, extension, created/modified dates).
  - `read_text_file`: Safe text reading across 25+ extensions (UTF-8 with Latin-1 fallback, 10MB cap, binary blocking).
  - `find_recent_files`: Identifies files modified within the past N days.
  - `find_large_files`: Identifies files exceeding a size threshold (MB), sorted largest first.
- **4 Controlled Modification Tools (Requires User Approval):**
  - `copy_file`: Destination existence and byte-size match verification.
  - `move_file`: Relocation with post-move verification (source removed, destination confirmed).
  - `rename_file`: In-place rename with path-injection protection.
  - `create_directory`: Validated directory creation.
- **Smart File Organization:**
  - `organize_files_preview`: Categorizes files (Documents, Images, Videos, Audio, Archives, Code, Other) and outputs a plan.
  - `organize_files`: Safely executes the organization plan with collision prevention.
- `ConfirmationCardWidget`: Interactive UI card in chat prompting users with `[Approve & Execute]` and `[Reject]` buttons.

#### ✅ Phase 2.2.3: Application & Process Control
- `AppDiscovery`: Discovers installed Windows applications from multiple sources:
  - Windows `App Paths` registry keys (`HKLM` & `HKCU`).
  - Windows Start Menu shortcuts (Common & User Start Menu `.lnk` files).
  - Windows `Uninstall` registry keys (DisplayIcon / InstallLocation).
  - Known built-in Windows utilities (Notepad, Calculator, Paint, Explorer, Terminal, PowerShell, CMD, Task Manager).
  - PATH executable search.
  - 1-hour cache TTL with thread-safe refresh.
- `AppNameResolver`: Natural language application resolution:
  - Standard alias dictionary (`VS Code` ➔ `Visual Studio Code`, `Chrome` ➔ `Google Chrome`, `calc` ➔ `Calculator`).
  - Case-insensitive substring and fuzzy matching (`difflib.SequenceMatcher`).
  - Ambiguity protection (returns candidate list when confidence is low).
- **5 Read-Only Tools (Auto-Approved):**
  - `search_applications`: Search installed apps by query/keyword with match scoring.
  - `list_installed_applications`: List discovered apps filtered optionally by category.
  - `list_running_processes`: List active processes with CPU %, memory in MB, and PID.
  - `check_application_status`: Check if an application is active with process count and aggregate memory.
  - `get_process_info`: Retrieve exact runtime metrics by name or specific PID.
- **4 Controlled Tools (Requires User Approval):**
  - `launch_application`: Launches desktop apps with shell injection prevention and PID verification.
  - `open_file_with_application`: Opens files with designated or default Windows applications within filesystem boundaries.
  - `open_folder`: Safely opens directory paths in Windows File Explorer.
  - `close_application`: Graceful termination (`SIGTERM` / `WM_CLOSE`), waits up to 2.5s, verifies exit.
- **Critical Process Guard:** Hard blacklist blocking termination of essential Windows infrastructure (`explorer.exe`, `svchost.exe`, `System`, `csrss.exe`, `dwm.exe`, `lsass.exe`) and the agent's own process.

#### ✅ Milestone A: Autonomous Computer Control Architecture & Safety Design
- Complete study and comparative analysis of three state-of-the-art reference repositories:
  1. **WindowsAgent** (Windows UI Automation, accessibility tree, UI grounding).
  2. **UI-TARS Desktop** (Visual computer control, normalized `[0, 1000]` coordinates, operator models).
  3. **AutoGUI** (ReAct loop, 4-tier safety model, action scoping, dry-run simulation, skill memory & replay).
- Created four exhaustive architectural specifications in `docs/`:
  - `docs/REFERENCE_REPOSITORY_ANALYSIS.md`: 12-dimension comparative analysis, 5-level interaction hierarchy, hardware budget for RTX 3050 6GB.
  - `docs/COMPUTER_AUTOMATION_ARCHITECTURE.md`: Complete subsystem design, `app/automation/` layout, data contracts (`DesktopObservation`, `ActionCommand`, `TaskPlan`).
  - `docs/SAFETY_MODEL.md`: 4-tier security taxonomy (`READ_ONLY`, `CONTROLLED`, `APPROVAL_REQUIRED`, `RESTRICTED`), window & path scoping, emergency abort (`Ctrl+Alt+X`, corner slam), SQLite audit schema.
  - `docs/AUTONOMOUS_TASK_EXECUTION.md`: Observe-Ground-Act-Verify (OGAV) ReAct loop, dynamic `TaskPlanner`, deterministic state assertions, loop bounds (max 25 steps, 10s action timeout, stall guard), skill replay memory.

---

## 4. Complete Project Directory Structure

```
h:\pro agent\
├── app/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── agent.py               # Main AgentCore & OllamaChatWorker (QThread)
│   │   ├── model_manager.py       # Ollama discovery, health & model parameters
│   │   ├── ollama_client.py       # Low-level HTTP client for Ollama API
│   │   └── task_manager.py        # Task queuing and execution state
│   ├── database/
│   │   ├── __init__.py
│   │   └── database.py            # SQLite schema initialization & repository methods
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── app_discovery.py       # Registry & Start Menu application scanner (cached)
│   │   ├── app_resolver.py        # Natural language alias & fuzzy resolver
│   │   ├── app_tools.py           # Phase 2.2.3 application & process control tools
│   │   ├── built_in_tools.py      # Time, system info, GPU info tools
│   │   ├── file_security.py       # Phase 2.2.2 filesystem boundary enforcer
│   │   ├── file_tools.py          # Phase 2.2.2 file search, read, copy, move, organize
│   │   ├── process_manager.py     # psutil process listing, status & graceful termination
│   │   ├── tool_executor.py       # 5-stage execution runner with timeout & timing
│   │   ├── tool_permissions.py    # Permission policies & confirmation requirements
│   │   ├── tool_registry.py       # In-memory tool registration catalog
│   │   └── tool_validator.py      # JSON Schema argument validation
│   └── ui/
│       ├── __init__.py
│       ├── main_window.py         # PySide6 MainWindow (Sidebar + Stack + Right Panel)
│       ├── components/
│       │   ├── __init__.py
│       │   ├── nav_sidebar.py     # Collapsible navigation rail
│       │   ├── right_panel.py     # Agent status, GPU monitor, task state
│       │   └── status_bar.py      # Bottom system telemetry bar
│       ├── pages/
│       │   ├── __init__.py
│       │   ├── chat_page.py       # Agent Chat UI, tool badges & confirmation cards
│       │   ├── home_page.py       # System dashboard & quick actions
│       │   ├── files_page.py      # File explorer view
│       │   ├── tasks_page.py      # Task management view
│       │   ├── browser_page.py    # Embedded browser view
│       │   ├── coding_page.py     # Code editor workspace
│       │   ├── workflows_page.py  # Node-based automation canvas
│       │   ├── voice_page.py      # Voice interaction view
│       │   ├── memory_page.py     # Agent memory inspector
│       │   ├── history_page.py    # Interaction history & logs
│       │   └── settings_page.py   # App settings & model controls
│       └── styles/
│           ├── __init__.py
│           └── theme.py           # Color palette, stylesheets & fonts
├── data/
│   └── agent_database.sqlite      # SQLite database file
├── docs/
│   ├── AUTONOMOUS_TASK_EXECUTION.md
│   ├── COMPUTER_AUTOMATION_ARCHITECTURE.md
│   ├── REFERENCE_REPOSITORY_ANALYSIS.md
│   └── SAFETY_MODEL.md
├── tests/
│   ├── test_app.py                # Phase 1 UI navigation & resize tests (6/6 pass)
│   ├── test_phase2.py             # Phase 2.1 Ollama & GPU benchmark tests (5/5 pass)
│   ├── test_phase2_2_1.py         # Phase 2.2.1 Tool engine unit tests (6/6 pass)
│   ├── test_phase2_2_2.py         # Phase 2.2.2 File intelligence tests (5/5 pass)
│   └── test_phase2_2_3.py         # Phase 2.2.3 App & process control tests (19/19 pass)
├── main.py                        # Application entry point
├── run_agent.bat                  # Windows launch script
├── README.md                      # Primary repository documentation
└── GPT_README.md                  # This file (LLM context briefing)
```

---

## 5. Active Database Schema (`data/agent_database.sqlite`)

The database uses SQLite 3 with WAL (Write-Ahead Logging) enabled.

```sql
-- 1. Conversational Messages
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('user', 'assistant', 'system', 'tool')),
    content TEXT NOT NULL,
    model TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT
);

-- 2. Tasks
CREATE TABLE IF NOT EXISTS tasks (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL,
    priority TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 3. Long-Term Memory
CREATE TABLE IF NOT EXISTS memory_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT NOT NULL UNIQUE,
    value TEXT NOT NULL,
    category TEXT DEFAULT 'general',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 4. Activity Logs
CREATE TABLE IF NOT EXISTS activity_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL,
    description TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    details TEXT
);

-- 5. Tool Execution Logs
CREATE TABLE IF NOT EXISTS tool_executions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tool_name TEXT NOT NULL,
    parameters TEXT,
    result TEXT,
    status TEXT NOT NULL,
    execution_time_ms REAL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Staged Automation Schema (Milestone A Specification)
To be added during Milestones F through H:
- `action_audit_log`: High-fidelity forensics recording target HWND, window title, UI selectors, safety tier, approval status, before/after state hashes.
- `skills` & `skill_steps`: Parameterized trajectory memory for zero-LLM replay of learned multi-step desktop workflows.

---

## 6. Automated Test Baseline (41 / 41 Tests Passing — 100%)

All features are covered by automated unit and integration tests. **Never commit changes that break any of these tests.**

```bash
# 1. Phase 2.2.3 Application & Process Control (19 tests)
python tests/test_phase2_2_3.py   --> 19 / 19 PASSED (OK in ~43s)

# 2. Phase 2.2.2 File Intelligence & Operations (5 tests)
python tests/test_phase2_2_2.py   --> 5 / 5 PASSED (OK)

# 3. Phase 2.2.1 Agent Tool Engine (6 tests)
python tests/test_phase2_2_1.py   --> 6 / 6 PASSED (OK)

# 4. Phase 2.1 Hardware, GPU & Model Streaming (5 tests)
python tests/test_phase2.py       --> 5 / 5 PASSED (OK)

# 5. Phase 1 Desktop UI Navigation & Layout (6 tests)
python tests/test_app.py          --> 6 / 6 PASSED (OK)

TOTAL: 41 / 41 TESTS PASSING (100% SUCCESS RATE)
```

---

## 7. Critical Implementation Insights & Known Gotchas

1. **Tool Confirmation Feedback Loop (Fixed):**
   - When a tool requires confirmation (e.g. `launch_application`, `close_application`, `copy_file`), the tool result returned to the model must have status `"staged_for_user_approval"` rather than an error string.
   - If an error string like `"User confirmation required"` is returned, Qwen hallucinated that it lacked desktop capabilities.
   - The Chat UI renders an amber badge (`🛡️ Action staged: Awaiting user approval`) with `[Approve]` and `[Reject]` buttons. When the user approves, the action executes immediately and posts confirmation.
2. **Windows Store Python Alias (`WindowsApps\python.exe`):**
   - On Windows 11, running `python.exe` via sandboxed environments can fail with `ResourceUnavailable: The file cannot be accessed by the system` because UWP AppExecutionAlias reparse points require full filesystem access.
   - Always run commands in standard mode first, and if UWP reparse fails, elevate with `BypassSandbox: true`.
3. **PowerShell Command Chaining:**
   - On Windows PowerShell, chaining commands with `&&` fails on older PS versions. Always use `;` to chain commands reliably (e.g. `cmd1 ; cmd2`).
4. **VRAM Boundary Protection:**
   - RTX 3050 has 6144 MiB physical VRAM. Ollama uses ~4218 MiB for `qwen3:8b` (`num_ctx: 4096`). Windows Desktop Window Manager (DWM) uses ~800 MiB.
   - Free headroom is ~1126 MiB. Do **not** load heavy vision models into GPU memory. Visual automation must use remote APIs or quantized CPU inference.

---

## 8. Autonomous Computer Control Roadmap Ahead

The project is structured into distinct, sequential milestones. **Do not jump ahead without user approval.**

- [x] **Milestone A: Architecture & Safety Specification** *(COMPLETE & COMMITTED)*
  - Reference analysis of WindowsAgent, UI-TARS Desktop, and AutoGUI.
  - 5-level interaction hierarchy & 4-tier safety model.
  - ReAct execution specifications (`docs/`).
- [ ] **Milestone B: Windows UI Automation Backend** *(NEXT STAGED)*
  - Implement `app/automation/uia/`: `uia_backend.py`, `tree_inspector.py`, `element_grounder.py`.
  - Native UI Automation tree traversal, accessibility pattern invocation (`InvokePattern`, `ValuePattern`).
  - Resilient to DPI and screen coordinate changes without VRAM usage.
- [ ] **Milestone C: Desktop Actions & Coordinate Grounding**
  - Implement `app/automation/actions/`: `input_simulator.py`, `window_manager.py`.
  - Normalized `[0, 1000]` coordinate mapping, Win32 `SendInput`, PyAutoGUI corner failsafe.
- [ ] **Milestone D: Browser Automation Backend**
  - Implement `app/automation/browser/`: `browser_controller.py`, `dom_locator.py`.
  - Playwright integration, semantic DOM locators, network idle synchronization.
- [ ] **Milestone E: Visual & OCR Fallback Engine**
  - Implement `app/automation/visual/`: `screen_capture.py`, `visual_grounder.py`, `ocr_engine.py`.
  - Configurable remote/CPU VLM interface, Windows Media OCR text bounding box centroids.
- [ ] **Milestone F: Autonomous Task Execution Engine**
  - Implement `app/automation/planner/`: `react_loop.py`, `task_planner.py`, `verification.py`.
  - Observe-Ground-Act-Verify loop, deterministic state assertions, loop bounds (max 25 steps, stall detection).
- [ ] **Milestone G: Safety, Scoping & Human Oversight**
  - Implement `app/automation/safety/`: `safety_enforcer.py`, `scope_guard.py`, `abort_controller.py`.
  - 4-tier security enforcement, window/path scoping, dry-run simulation mode, emergency abort (`Ctrl+Alt+X`).
- [ ] **Milestone H: Skill Memory & Trajectory Replay**
  - Implement `app/automation/planner/skill_store.py`.
  - SQLite `skills` schema, parameterized workflow templates, zero-LLM fast-path replay, self-repair.
- [ ] **Milestone I: Desktop UI Integration & End-to-End Testing**
  - Integrate live execution cards and abort buttons into PySide6 chat UI.
  - Comprehensive automated end-to-end testing across Windows applications.

---

## 9. Quick Guide for ChatGPT / GPT Continuing This Project

When continuing work on this repository:
1. **Read this file first (`GPT_README.md`)** to get the full picture.
2. **Current State:** Milestone A is 100% complete. We are ready to begin **Milestone B (Windows UI Automation Backend)** upon user confirmation.
3. **Execution Invariant:** Always write code that is modular, beginner-readable, PEP8-compliant, and fully typed (`typing.Optional`, `typing.Any`, etc.).
4. **Testing Invariant:** Always run the test suite (`python tests/test_phase2_2_3.py`) to verify zero regressions.
5. **UI Invariant:** Never modify the existing PySide6 theme colors or remove existing pages. All additions integrate smoothly into the existing layout.
