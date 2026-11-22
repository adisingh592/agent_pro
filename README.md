# Personal Agent — Desktop AI Assistant

A high-performance personal desktop AI assistant built with **Python 3.12+**, **PySide6**, and an **SQLite-ready modular architecture**, powered by **local Ollama LLMs with NVIDIA GPU hardware acceleration** and a **safe, extensible tool-calling execution engine**.

Inspired by VS Code, Antigravity, and modern developer workspaces, Personal Agent provides a centralized, professional command center designed for speed, visual clarity, and future autonomous desktop capabilities.

---

## 📌 Project Status: Milestone C Complete (Desktop Actions & Coordinate Grounding)

> **Current Milestone**: Milestone C — Desktop Actions & Coordinate Grounding (Complete & 100% Verified)  
> **Prior Completed Phases**: Phase 1 (UI Foundation), Phase 2.1 (Local AI & GPU), Phase 2.2.1 (Tool Engine), Phase 2.2.2 (File Operations), Phase 2.2.3 (App & Process Control), Milestone A (Architecture & Safety Design), Phase 2.3 / Milestone B (Windows UI Automation Engine)  
> **Target Hardware**: NVIDIA GeForce RTX 3050 Laptop GPU (6GB VRAM) / Intel Core i7-13650HX / 32GB RAM / Windows 11  
> **Model**: `qwen3:8b` (5.2 GB GGUF, Q4_K_M) via Ollama (`llamacpp` CUDA v12 runner)  
> **Repository**: [https://github.com/adisingh592/agent_pro.git](https://github.com/adisingh592/agent_pro.git)  

---

## 📑 Table of Contents

1. [Project Completion & Progress Tracker](#-project-completion--progress-tracker)
2. [Milestone C — Desktop Actions & Coordinate Grounding](#-milestone-c--desktop-actions--coordinate-grounding)
   - [Normalized Coordinate Grounding & DPI Mapping](#1-normalized-coordinate-grounding--dpi-mapping)
   - [Physical Input Simulation & Win32 Integration](#2-physical-input-simulation--win32-integration)
   - [Global Emergency Stop Circuit Breaker](#3-global-emergency-stop-circuit-breaker)
   - [Safety Confirmation Barriers & Keyboard Allowlists](#4-safety-confirmation-barriers--keyboard-allowlists)
   - [Automated Verification Tests](#5-automated-verification-tests)
3. [Phase 2.3 — Windows UI Automation Engine](#-phase-23--windows-ui-automation-engine)
   - [Technology Selection & Architecture](#1-technology-selection--architecture)
   - [Desktop Window Discovery & Management](#2-desktop-window-discovery--management)
   - [UI Element Inspection & Compact Observations](#3-ui-element-inspection--compact-observations)
   - [Intelligent Element Finding & Ambiguity Handling](#4-intelligent-element-finding--ambiguity-handling)
   - [Native Pattern Actions (Click, Type, Read, Keypress)](#5-native-pattern-actions-click-type-read-keypress)
   - [Security, Key Allowlists & Confirmation Staging](#6-security-key-allowlists--confirmation-staging)
   - [Full Automated Test Verification Suite](#7-full-automated-test-verification-suite)
4. [Autonomous Computer Automation Engine (Milestones A—I)](#-autonomous-computer-automation-engine-milestones-a-i)
5. [Phase 2.2.3 — Application & Process Control](#-phase-223--application--process-control)
6. [Phase 2.2.2 — File Intelligence & Safe File Operations](#-phase-222--file-intelligence--safe-file-operations)
7. [Phase 2.2.1 — Agent Tool Engine](#-phase-221--agent-tool-engine)
8. [Phase 2.1 — Local AI Integration & NVIDIA GPU Acceleration](#-phase-21--local-ai-integration--nvidia-gpu-acceleration)
9. [Application Layout & Pages](#-application-layout--pages)
10. [Project Structure](#-project-structure)
11. [Database Schema](#-database-schema)
12. [Getting Started & Installation](#-getting-started--installation)
13. [Verification & Benchmark Tests](#-verification--benchmark-tests)
14. [Roadmap Ahead](#-roadmap-ahead)

---

## 📊 Project Completion & Progress Tracker

### Overall Phase Completion Matrix

| Milestone | Scope / Capabilities | Status | Completion |
| :--- | :--- | :---: | :---: |
| **Phase 1: Desktop UI Foundation** | PySide6 3-part layout, 11 navigation pages, dark charcoal/amber theme, SQLite setup, high-DPI scaling. | ✅ Complete | **100%** |
| **Phase 2.1: Local AI Integration** | Ollama local daemon API, `qwen3:8b` discovery, NVIDIA RTX 3050 6GB GPU acceleration (70% offload), non-blocking token streaming, chat history. | ✅ Complete | **100%** |
| **Phase 2.2.1: Agent Tool Engine** | 5-stage tool execution pipeline, JSON Schema validation, permissions policy, multi-round tool loop, chat tool badges, 3 built-in safe tools. | ✅ Complete | **100%** |
| **Phase 2.2.2: File Operations** | File search, list, metadata, text reading, recent/large files, verified copy/move/rename/mkdir, interactive confirmation UI, smart organization. | ✅ Complete | **100%** |
| **Phase 2.2.3: App & Process Control** | Multi-source app discovery, natural language resolver, safe process inspection, controlled launch, graceful close, critical process guard. | ✅ Complete | **100%** |
| **Milestone A: Architecture & Safety** | Reference analysis of WindowsAgent, UI-TARS, AutoGUI; 5-level hybrid architecture; 4-tier safety model; ReAct execution specs. | ✅ Complete | **100%** |
| **Phase 2.3 / Milestone B: Windows UI Automation** | Desktop window discovery, accessibility tree inspection, element finding, native pattern invocation (Invoke/Value/Toggle), key allowlists, confirmation staging. | ✅ Complete | **100%** |
| **Milestone C: Desktop Actions & Grounding** | Normalized coordinate mapping [0, 1000], DPI scaling, virtual screen multi-monitor geometry, physical mouse/keyboard simulation, corner slam failsafe, 11 tools. | ✅ Complete | **100%** |
| **Milestone D: Browser Automation Backend** | Playwright / Chrome DevTools Protocol integration, semantic DOM locators, network idle detection, form automation. | ⏳ Staged (Next) | **0%** |
| **Milestone E: Visual & OCR Fallback Engine** | Configurable lightweight/remote VLM interface, Windows Media OCR / Tesseract fallback for canvas/Direct3D applications. | ⏳ Staged | **0%** |
| **Milestone F: Autonomous Task Execution Engine**| Closed-loop Observe-Ground-Act-Verify ReAct loop, dynamic TaskPlanner, deterministic state assertions, stall detection. | ⏳ Staged | **0%** |
| **Milestone G: Safety, Scoping & Human Oversight**| 4-tier security enforcer, application scoping, dry-run simulation mode, emergency abort (Ctrl+Alt+X), SQLite action audit logging.| ⏳ Staged | **0%** |
| **Milestone H: Skill Memory & Trajectory Replay**| Parameterized skill storage, SQLite `skills` schema, fast-path zero-LLM replay, drift detection and self-repair. | ⏳ Staged | **0%** |
| **Milestone I: Desktop UI Integration & E2E Tests**| Live execution cards, step-by-step progress drawer, abort button, interactive approval cards, comprehensive test suite. | ⏳ Staged | **0%** |

```
[Phase 1]       ████████████████████ 100% Complete
[Phase 2.1]     ████████████████████ 100% Complete
[Phase 2.2.1]   ████████████████████ 100% Complete
[Phase 2.2.2]   ████████████████████ 100% Complete
[Phase 2.2.3]   ████████████████████ 100% Complete
[Milestone A]   ████████████████████ 100% Complete (Architectural Specification Ready)
[Phase 2.3]     ████████████████████ 100% Complete (Windows UI Automation Engine)
[Milestone C]   ████████████████████ 100% Complete (Desktop Actions & Coordinate Grounding)
[Milestones D-I]░░░░░░░░░░░░░░░░░░░░   0% Staged (Awaiting User Review & Approval)
```

---

## 🖱️ Milestone C — Desktop Actions & Coordinate Grounding

Personal Agent provides physical desktop mouse and keyboard interaction capabilities grounded in a standardized coordinate space. When target applications do not expose accessible UI Automation controls (e.g., custom rendering canvases, games, legacy apps), the agent can interact reliably via physical input simulation with comprehensive safety boundaries.

### 1. Normalized Coordinate Grounding & DPI Mapping
- **Normalized Scale `[0, 1000]`**: All coordinates exchanged with the LLM are expressed on a resolution-independent `[0, 1000]` grid, where `(0, 0)` is top-left and `(1000, 1000)` is bottom-right.
- **Multi-Monitor Virtual Screen Geometry**: Automatically detects primary resolution, virtual desktop offsets (`SM_XVIRTUALSCREEN`, `SM_YVIRTUALSCREEN`), and multi-monitor span (`SM_CXVIRTUALSCREEN`, `SM_CYVIRTUALSCREEN`).
- **DPI Scaling Support**: Reads system DPI via Win32 `GetDpiForSystem()` and scales coordinate conversions automatically.
- **Window-Relative Mapping**: When a `window_title` is provided, coordinates map relative to that window's bounding box rectangle rather than the entire desktop.

### 2. Physical Input Simulation & Win32 Integration
- **Mouse Primitives**:
  - `move_mouse(x, y, normalized, window_title)`: Smooth cursor movement.
  - `click_at(x, y, button, normalized, window_title)`: Left, right, and middle clicks with verified cursor position.
  - `double_click_at(x, y, normalized, window_title)`: Rapid double-click sequence.
  - `right_click_at(x, y, normalized, window_title)`: Context menu activation.
  - `drag_mouse(start_x, start_y, end_x, end_y, duration_ms, normalized, window_title)`: Click-and-drag with synthetic movement interpolation.
  - `scroll_at(wheel_units, horizontal, x, y, normalized, window_title)`: Vertical and horizontal mouse wheel scrolling.
- **Keyboard Primitives**:
  - `type_desktop_text(text, window_title, delay_per_char)`: Simulates real typing with configurable per-character delay (`delay_per_char=0.01s`). Does NOT automatically press Enter. Text is masked in logs for privacy.
  - `press_desktop_key(key, window_title, approved_key_combination)`: Dispatches safe functional keys (`Tab`, `Escape`, `Enter`, `F1-F12`, arrow keys) and shortcuts (`Ctrl+C`, `Ctrl+V`, `Ctrl+S`).

### 3. Global Emergency Stop Circuit Breaker
- **Failsafe Corner Slam**: Moving or dragging the cursor into the extreme top-left corner `(0, 0)` or `<= 5px` immediately trips the global emergency stop circuit breaker.
- **Hardware Button & Modifier Release**: On trigger, dispatches synthetic `LEFTUP`, `RIGHTUP`, `MIDDLEUP`, and `Shift`/`Ctrl`/`Alt`/`Win` key releases to eliminate sticky key states.
- **Latching Action Rejection**: Once tripped, all subsequent physical actions are rejected with `EMERGENCY_STOP_ACTIVE`.
- **Deliberate Reset Barrier**: Requires explicit call to `reset_emergency_stop` confirmed by the user.

### 4. Safety Confirmation Barriers & Keyboard Allowlists
- **Tier 3 Human-in-the-Loop Confirmation**: All mutating desktop actions require user confirmation before execution.
- **Auto-Approved Telemetry**: `get_screen_metrics` and `trigger_emergency_stop` are auto-approved for zero-friction safety.
- **Allowlist Filtering**: Keys outside `SAFE_KEYS` and `SENSITIVE_KEYS` are rejected with `KEY_NOT_ALLOWED`.

### 5. Automated Verification Tests
- **23 dedicated tests** in `tests/test_milestone_c_desktop_actions.py` covering coordinate mapping, DPI scaling, mouse moves, clicks, typing, key combinations, emergency stop, and confirmation staging.
- **All 23 tests pass in 0.006s** using mocks (zero disruption to the user's active desktop during testing).

---

## 🪟 Phase 2.3 — Windows UI Automation Engine

Personal Agent is equipped with a high-reliability **Windows UI Automation Engine** built with `uiautomation` and `pywin32`. This enables the agent to understand and interact with Windows desktop applications through their native accessible UI controls, rather than relying on brittle pixel coordinates.

### 1. Technology Selection & Architecture
- **Primary Backend**: `uiautomation>=2.0.29` (native Microsoft UI Automation COM interface) + `pywin32>=312` (`win32gui`, `win32process`, `win32con`).
- **Core Architecture** (`app/automation/`):
  - `automation_models.py`: Data models (`WindowInfo`, `UIElementInfo`, `ElementMatch`, `AutomationResult`).
  - `window_manager.py`: High-performance window enumeration, PID/process extraction, active window tracking, foreground activation with minimize restoration.
  - `element_inspector.py`: Bounded tree traversals (configurable `maximum_depth` and `maximum_elements`), property extraction, and token-efficient compact observation layer.
  - `element_finder.py`: Intelligent multi-tier control matching (exact AutomationId, exact name, case-insensitive, substring, fuzzy) with ambiguity detection.
  - `action_executor.py`: Native pattern actions (`InvokePattern`, `ValuePattern`, `TogglePattern`, `SelectionItemPattern`), bounding center fallback, password masking, and keyboard allowlists.
  - `windows_automation.py`: Unified automation engine coordinator.
  - `app/tools/ui_automation_tools.py`: Tool wrappers and registration with `ToolRegistry`.

### 2. Available UI Automation Tools (9 New Tools)

| Tool Name | Parameters | Permission Level | Description |
| :--- | :--- | :---: | :--- |
| `list_windows` | `visible_only`, `maximum_results` | `SAFE_READ_ONLY` (Auto) | List open desktop windows with title, PID, visibility, and minimized/maximized state. |
| `get_active_window` | *(none)* | `SAFE_READ_ONLY` (Auto) | Return title, PID, process name, and bounds of the foreground window. |
| `inspect_window` | `window_title`, `maximum_depth`, `maximum_elements` | `SAFE_READ_ONLY` (Auto) | Traverse accessibility tree of target window and produce a compact summary. |
| `find_ui_element` | `window_title`, `element_name`, `control_type`, `automation_id` | `SAFE_READ_ONLY` (Auto) | Search for buttons, text boxes, and menus in a window by label or ID with ambiguity alerts. |
| `click_ui_element` | `window_title`, `element_name`, `control_type`, `automation_id`, `match_index` | `CONTROLLED_ACTION` (Staged) | Click or invoke interactive UI controls using native patterns. Staged for user confirmation. |
| `type_into_ui_element`| `window_title`, `element_name`, `text`, `automation_id`, `match_index` | `CONTROLLED_ACTION` (Staged) | Enter text into text inputs via `ValuePattern.SetValue` or keystrokes. Staged for confirmation. |
| `read_ui_element` | `window_title`, `element_name`, `control_type`, `automation_id` | `SAFE_READ_ONLY` (Auto) | Read text or value of a control. Automatically masks passwords and sensitive tokens (`********`). |
| `focus_window` | `window_title`, `process_name`, `process_id` | `CONTROLLED_ACTION` (Auto) | Restore if minimized and bring target window to the foreground. |
| `press_key` | `window_title`, `key`, `approved_key_combination` | `CONTROLLED_ACTION` (Policy) | Send approved keyboard shortcuts. Sensitive shortcuts (`Alt+F4`, `Enter`) require confirmation. |

### 3. Keyboard Allowlist & Safety Invariants
- **Safe Keys (Approved)**: `Escape`, `Tab`, `Space`, `Backspace`, `Delete`, `Up`, `Down`, `Left`, `Right`, `Home`, `End`, `PageUp`, `PageDown`, `F1`–`F12`, `Ctrl+A`, `Ctrl+C`, `Ctrl+V`, `Ctrl+X`, `Ctrl+Z`, `Ctrl+Y`, `Ctrl+S`, `Ctrl+F`.
- **Sensitive Keys (Confirmation Required)**: `Enter`, `Return`, `Alt+F4`, `Ctrl+W`, `Ctrl+Shift+Esc`.
- **Arbitrary Key Blocking**: Random strings or unvalidated keys are strictly rejected with `KEY_NOT_ALLOWED`.
- **Disabled Element Protection**: Elements reporting `IsEnabled: False` cannot be clicked or typed into.
- **Ambiguity Guard**: When a query matches multiple elements with similar confidence, the tool halts and lists candidates rather than guessing.

### 4. Automated Test Verification (20 / 20 Tests Passed — 100%)
```bash
python tests/test_phase2_3_windows_ui_automation.py
```
**Test Results**:
```text
test_action_executor_disabled_element_protection ... ok
test_click_ui_element_requires_confirmation_in_executor ... ok
test_compact_observation_generation ... ok
test_controlled_action_requires_confirmation ... ok
test_element_matching_logic_mocked ... ok
test_find_element_in_nonexistent_window ... ok
test_find_window_exact_and_substring ... ok
test_find_window_nonexistent_returns_none ... ok
test_get_active_window ... ok
test_get_active_window_executor_execution ... ok
test_inspect_window_nonexistent ... ok
test_key_allowlist_enforcement ... ok
test_list_windows_executor_execution ... ok
test_list_windows_respects_max_results ... ok
test_list_windows_returns_structured_data ... ok
test_phase2_3_tools_registered ... ok
test_press_key_requires_confirmation_in_executor ... ok
test_read_element_sensitive_masking ... ok
test_read_only_automation_tools_auto_approved ... ok
test_safe_keys_recognized ... ok
----------------------------------------------------------------------
Ran 20 tests in 0.002s - OK (100% Passing)
```

---

## 🤖 Autonomous Computer Automation Engine (Milestones A—I)

Personal Agent is evolving from an intelligent conversational agent with file and process capabilities into a **unified autonomous computer-use agent**, synthesizing key architectural paradigms from three state-of-the-art open-source projects:

1. **[WindowsAgent](https://github.com/ibraheem-mustafa-dev/windowsagent)**: Windows UI Automation tree inspection, accessibility patterns, window discovery, and deterministic UI grounding.
2. **[UI-TARS Desktop](https://github.com/bytedance/UI-TARS-desktop)**: Visual computer control, normalized `[0, 1000]` coordinates, multimodal visual grounding fallback, and cross-platform operator abstractions.
3. **[AutoGUI](https://github.com/BillJr99/AutoGUI)**: Observe-Ground-Act-Verify ReAct loop, 4-tier safety model, action scoping, dry-run simulation mode, persistent skill memory, and trajectory replay.

### Architectural Deliverables & Specifications

The engineering blueprints for this evolutionary milestone have been formalized into dedicated specifications:

| Specification Document | Focus Area & Key Technical Invariants |
| :--- | :--- |
| **[docs/REFERENCE_REPOSITORY_ANALYSIS.md](file:///h:/pro%20agent/docs/REFERENCE_REPOSITORY_ANALYSIS.md)** | Comparative analysis across 12 architectural dimensions, 5-level interaction priority matrix, VRAM/RAM hardware budget for RTX 3050 6GB, and licensing compliance. |
| **[docs/COMPUTER_AUTOMATION_ARCHITECTURE.md](file:///h:/pro%20agent/docs/COMPUTER_AUTOMATION_ARCHITECTURE.md)** | End-to-end subsystem layout, `app/automation/` modular package hierarchy, data models (`DesktopObservation`, `ActionCommand`, `TaskPlan`), and system integration. |
| **[docs/SAFETY_MODEL.md](file:///h:/pro%20agent/docs/SAFETY_MODEL.md)** | 4-tier security classification (`READ_ONLY`, `CONTROLLED`, `APPROVAL_REQUIRED`, `RESTRICTED`), window & path scoping, dry-run simulation, emergency abort (`Ctrl+Alt+X`, corner slam), and SQLite audit logging. |
| **[docs/AUTONOMOUS_TASK_EXECUTION.md](file:///h:/pro%20agent/docs/AUTONOMOUS_TASK_EXECUTION.md)** | Observe-Ground-Act-Verify (OGAV) ReAct loop, dynamic `TaskPlanner`, deterministic state assertions, loop bounds (max 25 steps, 10s action timeout, stall guard), and parameterized skill replay memory. |

### 5-Level Hybrid Interaction Priority Matrix

To maximize reliability and performance on our target hardware without exhausting VRAM, Personal Agent dispatches operations through a hierarchical priority cascade:

1. **Level 1: System & Application APIs (Fastest & 100% Deterministic — 0 VRAM)**: Built-in `file_tools`, `app_tools`, `process_manager`, Win32 API.
2. **Level 2: Windows UI Automation Tree (Accessibility-First — 0 VRAM)**: Native UI Automation pattern invocation (`InvokePattern`, `ValuePattern`), resilient against DPI, layout, and window coordinate changes.
3. **Level 3: Structured Browser DOM (Playwright & CDP — 0 VRAM)**: Semantic CSS/XPath locators, DOM element grounding, and network idle verification for web applications.
4. **Level 4: Multimodal Visual Grounding (Complementary Fallback — Configurable Endpoint)**: Screenshot-based bounding box and coordinate prediction for custom-rendered canvas or Direct3D applications.
5. **Level 5: Local OCR Fallback (Text Bounding Box Centroids — CPU / Zero VRAM)**: Windows Media OCR or Tesseract text box centroid targeting when UI elements lack accessibility descriptors.

---

### What Is Working Right Now (Verified Capabilities)

1. **🖥️ Desktop UI (Phase 1 — 100% Verified)**:
   - Full 3-part layout: Collapsible left navigation sidebar, center multi-view stack, persistent right agent monitoring panel, and bottom system status bar.
   - **All 11 Dedicated Pages Active**: Home, Agent Chat, Tasks, Files, Browser, Coding Workspace, Workflows, Voice Assistant, Memory, History, and Settings.
   - Professional dark charcoal (`#181a1f`) and neutral gray surfaces with restrained warm amber (`#e59840`) accents.

2. **🧠 Local AI & GPU Acceleration (Phase 2.1 — 100% Verified)**:
   - Direct integration with local Ollama (`http://localhost:11434`) using `qwen3:8b` (5.2 GB GGUF).
   - **70% GPU Offload / 30% CPU Offload** verified on NVIDIA RTX 3050 Laptop GPU (6GB VRAM) by bounding context window to `num_ctx: 4096`.
   - **18.3 – 20.4 tokens/second** generation speed with 4,218 MiB VRAM dedicated to Ollama.
   - Progressive token streaming via background `QThread` (`OllamaChatWorker`), reasoning `<think>` token handling, and instant stop generation (`⏹`).

3. **⚙️ Agent Tool Engine (Phase 2.2.1 — 100% Verified)**:
   - **5-Stage Tool Pipeline**: Request → Schema Validation → Permission Policy Check → Isolated Execution with Duration Timing → Natural Language Analysis.
   - Multi-round tool execution loop (up to 5 rounds) with structured JSON fallback.
   - Real-time `ToolActivityWidget` cards embedded in chat showing tool status, duration, and success/failure badges.

4. **📁 File Intelligence & Safe File Operations (Phase 2.2.2 — 100% Verified)**:
   - **Filesystem Safety Guard**: Strict blocking of `C:\Windows`, `System32`, `Program Files`, and `ProgramData`. Traversal protection (`..` escape prevention). Canonical resolution.
   - **6 Read-Only Tools (Auto-Approved)**:
     - `search_files`: Wildcard file search (`*.py`, `*report*`) with 500-result limit and recursive traversal.
     - `list_directory`: Folder listing with file/directory classification, sizes, and timestamps.
     - `get_file_info`: Metadata extraction (full path, size, extension, created/modified dates).
     - `read_text_file`: Safe text reading across 25+ extensions (UTF-8 with Latin-1 fallback, 10MB cap, binary blocking).
     - `find_recent_files`: Finds files modified within the past N days.
     - `find_large_files`: Identifies files exceeding a size threshold (MB), sorted largest first.
   - **4 Controlled Modification Tools (Requires User Approval)**:
     - `copy_file`: Destination existence and size match verification.
     - `move_file`: Relocation with post-move verification (source removed, destination confirmed).
     - `rename_file`: In-place rename with path-injection protection.
     - `create_directory`: Validated folder creation.
   - **Smart File Organization**:
     - `organize_files_preview`: Analyzes files and generates proposed category plans (Documents, Images, Videos, Audio, Archives, Installers, Code, Other).
     - `organize_files`: Safely moves files into categorized subfolders without overwrite conflicts.
   - **Interactive Confirmation UI**: `ConfirmationCardWidget` embedded in chat prompting users with `[Approve & Execute]` and `[Reject]` actions for all write operations.

5. **🖥️ Application & Process Control (Phase 2.2.3 — 100% Verified)**:
   - **Multi-Source Application Discovery**: Discovers installed applications from Windows `App Paths` registry, Start Menu shortcuts, `Uninstall` registry keys, known built-in utilities (Notepad, Calculator, Paint, File Explorer, Terminal, PowerShell, CMD, Task Manager), and PATH binaries with a 1-hour cache TTL.
   - **Natural Language Application Name Resolution**: Standard alias resolution (e.g. `VS Code` → `Visual Studio Code`, `Chrome` → `Google Chrome`, `calc` → `Calculator`), fuzzy matching, and strict ambiguity protection (returns candidate choices for user clarification when ambiguous).
   - **5 Read-Only Tools (Auto-Approved)**:
     - `search_applications`: Searches installed applications by query or category keyword with match confidence scoring.
     - `list_installed_applications`: Lists discovered applications filtered optionally by category (Development, Browser, Media, Productivity, System, Other).
     - `list_running_processes`: Lists active Windows processes with CPU %, memory in MB, status, and PID sorting/filtering without leaking environment secrets.
     - `check_application_status`: Verifies whether an application (e.g. Ollama, Chrome, VS Code) is running with aggregate memory usage and process count.
     - `get_process_info`: Queries comprehensive process runtime metrics by name or specific PID.
   - **4 Controlled Actions (Requires User Approval)**:
     - `launch_application`: Launches registered Windows desktop applications with strict shell injection prevention and PID verification.
     - `open_file_with_application`: Opens files with specified application or default Windows association while respecting filesystem boundaries.
     - `open_folder`: Safely opens directory paths in Windows File Explorer.
     - `close_application`: Gracefully terminates application processes (`SIGTERM` / `WM_CLOSE`), waits up to 2.5s, verifies exit, and blocks critical Windows system processes.
   - **Security Restriction Guard**: Hard blacklist preventing termination of critical Windows infrastructure (`explorer.exe`, `svchost.exe`, `System`, `csrss.exe`, `dwm.exe`, etc.) and the agent's own process.

6. **🗄️ Database & Storage (100% Verified)**:
   - SQLite database (`data/agent_database.sqlite`) with 5 active tables: `messages`, `tasks`, `memory_items`, `activity_logs`, and `tool_executions`.
   - Comprehensive audit logging recording tool names, arguments, results, verification status, and execution durations.

7. **📊 Automated Test Coverage (41 / 41 Tests Passing — 100%)**:
   - `tests/test_phase2_2_3.py`: **19 / 19 PASSED** (Discovery, caching, exact/alias/fuzzy/ambiguous resolution, launch validation, shell injection guard, open file/folder, process listing/filtering, application status, process info, critical process guard, graceful close verification, tool executor integration)
   - `tests/test_phase2_2_2.py`: **5 / 5 PASSED** (Filesystem safety, read-only tools, modifications with verification, organization, database auditing)
   - `tests/test_phase2_2_1.py`: **6 / 6 PASSED** (Registry, Validation, Tools, Permissions, SQLite logging, Live Round-Trip)
   - `tests/test_phase2.py`: **5 / 5 PASSED** (Ollama online, `qwen3:8b` detected, RTX 3050 6GB stats, 18.5 tok/s inference, stop mechanism)
   - `tests/test_app.py`: **6 / 6 PASSED** (All 11 UI pages navigation, resizing responsiveness, theme consistency)

---

## 🌟 Features Overview

| Feature Area | Description | Status |
| :--- | :--- | :---: |
| **Modern Desktop UI** | Dark charcoal developer theme (VS Code/Antigravity style) with amber pill accents, high-DPI scaling, and zero flickering. | ✅ Complete |
| **3-Part Workspace** | Left collapsible navigation sidebar, dynamic center view stack, persistent right agent status panel, and bottom system status bar. | ✅ Complete |
| **11 Dedicated Views** | Home, Agent Chat, Tasks, Files, Browser, Coding Workspace, Workflows, Voice, Memory, History, and Settings. | ✅ Complete |
| **Local LLM Engine** | Direct integration with local Ollama service (`http://localhost:11434`) without external cloud dependencies. | ✅ Complete |
| **NVIDIA GPU Offloading** | 70% GPU / 30% CPU hybrid layer distribution on RTX 3050 6GB; ~18.3–20.4 tokens/second generation speed. | ✅ Complete |
| **Live Token Streaming** | Progressive text emission via asynchronous `QThread` worker; supports both reasoning `<think>` tokens and final content. | ✅ Complete |
| **Agent Tool Engine** | Safe, multi-round tool calling pipeline with JSON schema validation, permissions, and timeout containment. | ✅ Complete |
| **Built-in System Tools** | Real-time system inspection: `get_current_time`, `get_system_info`, `get_gpu_info`. | ✅ Complete |
| **Filesystem Safety Guard** | Hard blocks on `C:\Windows`, `System32`, `Program Files`, traversal protection, and canonical path resolution. | ✅ Complete |
| **Read-Only File Tools** | 6 auto-approved tools: `search_files`, `list_directory`, `get_file_info`, `read_text_file`, `find_recent_files`, `find_large_files`. | ✅ Complete |
| **Controlled File Writes** | Verified `copy_file`, `move_file`, `rename_file`, `create_directory` with strict post-execution verification. | ✅ Complete |
| **Smart File Organization** | Preview-first category sorting (`organize_files_preview`, `organize_files`) across Documents, Images, Code, etc. | ✅ Complete |
| **Application Discovery** | Multi-source scanning (App Paths, Start Menu, Uninstall registry, PATH) with intelligent 1-hour cache TTL. | ✅ Complete |
| **Name Resolution Engine** | Alias mapping, fuzzy matching, and ambiguity guard prompting user clarification when multiple apps match. | ✅ Complete |
| **Process Inspection** | Safe process enumeration, status tracking, CPU % and memory monitoring without credential exposure. | ✅ Complete |
| **Controlled App Launching** | Safe `subprocess` launching without `shell=True`, argument sanitization, and post-launch PID verification. | ✅ Complete |
| **Graceful Process Closure** | Non-destructive `terminate()` shutdown with 2.5s verification and hard blocking of critical system processes. | ✅ Complete |
| **Interactive Confirmation UI** | In-chat `ConfirmationCardWidget` requiring explicit `[✓ Approve & Execute]` or `[✕ Reject]` for disk writes, app launch, and process termination. | ✅ Complete |
| **Instant Interruption** | Responsive "Stop Generating" (`⏹`) control that cancels network socket operations and tool execution immediately. | ✅ Complete |
| **Persistent Storage** | SQLite-backed database storing tasks, memories, activity history, chat messages, and tool executions. | ✅ Complete |
| **Live Hardware Monitor** | Background polling of CPU %, RAM %, GPU utilization %, VRAM allocation, and GPU temperature. | ✅ Complete |

---

## 🖥️ Phase 2.2.3 — Application & Process Control

Phase 2.2.3 empowers Personal Agent with the ability to discover, launch, monitor, inspect, and safely manage Windows desktop applications and processes through a unified, permission-gated tool engine.

```text
       User Natural Language Request ("Launch VS Code", "Is Ollama running?", "Close Spotify")
                                          │
                                          ▼
                                   Agent Core & LLM
                                          │
                                          ▼
                         Application & Process Tool Selection
                                          │
                  ┌───────────────────────┴───────────────────────┐
                  ▼                                               ▼
         [READ-ONLY TOOLS]                               [CONTROLLED ACTIONS]
  • search_applications                           • launch_application
  • list_installed_applications                   • open_file_with_application
  • list_running_processes                        • open_folder
  • check_application_status                      • close_application
  • get_process_info                                              │
                  │                                               ▼
                  │                                  [ConfirmationCardWidget in Chat]
                  │                                  [✕ Reject]   [✓ Approve & Execute]
                  │                                               │
                  └───────────────────────┬───────────────────────┘
                                          ▼
                             [Tool Execution & Verification]
                                          │
                                          ▼
                          [Natural Language Agent Response]
```

---

### 1. Application Discovery & Registry Cache

Rather than performing slow, exhaustive disk scans across entire drives, Personal Agent aggregates verified Windows application sources with an intelligent 1-hour cache (`CACHE_TTL_SECONDS = 3600.0`):

1. **Registry App Paths**: Inspects `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths` and `HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths` for registered application binaries (Chrome, VS Code, Brave, Firefox, Excel, etc.).
2. **Start Menu Shortcuts**: Recursively scans user shortcuts (`%APPDATA%\Microsoft\Windows\Start Menu\Programs`) and machine shortcuts (`%PROGRAMDATA%\Microsoft\Windows\Start Menu\Programs`), ignoring uninstallers, documentation, and help links.
3. **Registry Uninstall Catalog**: Queries `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall` (both 64-bit and WOW6432Node) and `HKCU` to resolve installed software display names and executable icons.
4. **Known Windows System Utilities**: Pre-configured instant access to standard utilities (`notepad.exe`, `calc.exe`, `mspaint.exe`, `explorer.exe`, `cmd.exe`, `powershell.exe`, `taskmgr.exe`, `regedit.exe`).
5. **System PATH Executables**: Resolves developer CLI tools (`ollama`, `wt`, `code`, `git`, `python`).

Each application is classified into standardized categories: **Development**, **Browser**, **Media**, **Productivity**, **System**, or **Other**.

---

### 2. Natural Language Application Name Resolution

The `ApplicationResolver` handles varied user phrasing with a multi-stage matching hierarchy:
- **Normalization**: Strips `.exe`, command prefixes (`open`, `launch`, `start`), and punctuation.
- **Alias Mapping**: Recognizes common variations (e.g. `VS Code` / `Code` → `Visual Studio Code`, `Chrome` → `Google Chrome`, `Edge` → `Microsoft Edge`, `calc` → `Calculator`, `terminal` → `Windows Terminal`, `ps` → `PowerShell`).
- **Exact & Substring Matching**: Matches primary names and verified aliases.
- **Fuzzy Matching (`difflib`)**: Resolves minor user typos (confidence ≥ 0.65).
- **Ambiguity Guard**: When a query matches multiple applications with close scores (e.g., `"Visual Studio"` matching both *Visual Studio Code* and *Visual Studio 2022*), the agent does **not** guess; it returns candidate choices asking the user for clarification.

---

### 3. Read-Only Application & Process Tools (Auto-Approved)

| Tool Name | Parameters | Description |
| :--- | :--- | :--- |
| **`search_applications`** | `query`, `maximum_results` | Searches installed applications by name or category keyword with confidence scoring. |
| **`list_installed_applications`** | `category`, `maximum_results` | Lists discovered desktop applications filtered optionally by category. |
| **`list_running_processes`** | `filter`, `maximum_results`, `sort_by` | Lists active processes with PID, memory (MB/readable), CPU %, and status. Never exposes passwords or env secrets. |
| **`check_application_status`** | `application_name` | Verifies whether an application is currently running, aggregating memory usage across worker processes. |
| **`get_process_info`** | `process_name`, `optional_pid` | Retrieves runtime statistics (CPU %, memory, start timestamp, status) for a specific process. |

---

### 4. Controlled Application Launching & File Associations

All launch and folder opening tools require explicit user approval (`CONTROLLED_ACTION`):

| Tool Name | Action | Verification Rule |
| :--- | :--- | :--- |
| **`launch_application`** | Launches a verified application executable or shortcut. | Validates target existence, strips dangerous shell injection characters (`&`, `\|`, `;`, `$`), runs with `shell=False`, and verifies process creation with PID. |
| **`open_file_with_application`** | Opens a file using a designated app or default Windows handler. | Enforces `FilesystemSafety.validate_read_path` boundaries, confirms file existence, and launches safely. |
| **`open_folder`** | Opens a directory in Windows File Explorer. | Validates directory existence, checks safety boundaries, and launches `explorer.exe`. |

---

### 5. Safe Process Management & Graceful Termination

The `close_application` tool implements safe process management:
1. **Resolution & PID Mapping**: Identifies all active child and worker PIDs associated with the application.
2. **Interactive Confirmation**: Prompts the user with `[✕ Reject]` and `[✓ Approve & Execute]` showing target PIDs and warning about potential unsaved work.
3. **Graceful Termination**: Uses `proc.terminate()` (`WM_CLOSE` / `SIGTERM`), **never** forcing termination initially.
4. **Post-Termination Verification**: Waits up to 2.5 seconds with `psutil.wait_procs()`. If the process exits, reports success. If it remains alive, reports graceful shutdown failure without escalating to force-kill.

---

### 6. Security Restrictions & Critical Process Protection

To protect system integrity, `ProcessManager.is_critical_process()` hard-blocks termination attempts against critical Windows operating system components and the Personal Agent itself:

```text
Protected Critical Processes:
  • System (PID 4)             • dwm.exe (Desktop Window Manager)
  • smss.exe (Session Manager) • explorer.exe (Windows Shell)
  • csrss.exe (Client/Server)  • taskhostw.exe (Host Process)
  • wininit.exe                • sihost.exe / shellexperiencehost.exe
  • services.exe               • securityhealthservice.exe / msmpeng.exe
  • lsass.exe                  • Personal Agent Process (os.getpid() & parent)
  • svchost.exe
```

Attempting to close any of these processes is rejected immediately with a `Security restriction` error.

---

## 📁 Phase 2.2.2 — File Intelligence & Safe File Operations

Phase 2.2.2 elevates Personal Agent into a capable, filesystem-aware desktop assistant. It can discover, inspect, read, organize, and manipulate local files while maintaining absolute security boundaries and requiring user confirmation for every modification.

### 1. Filesystem Safety Architecture & Boundaries

All file requests must pass through `FilesystemSafety` (`app/tools/filesystem_safety.py`):
- **Canonical Path Resolution**: Uses `Path(p).resolve()` to eliminate relative `..` segments and symlinks.
- **Restricted System Directories**: Automated operations are completely blocked from accessing or altering:
  - Windows installation directories (`C:\Windows`, `C:\Windows\System32`, `C:\Windows\SysWOW64`)
  - Application binaries (`C:\Program Files`, `C:\Program Files (x86)`, `C:\ProgramData`)
  - Recovery, `$Recycle.Bin`, System Volume Information, and boot partitions.
- **Allowed Workspaces**: User-selected folders, workspace directories, and common folders (Desktop, Documents, Downloads, Pictures).

---

### 2. Read-Only File Tools (Auto-Approved)

| Tool Name | Parameters | Description |
| :--- | :--- | :--- |
| **`search_files`** | `directory`, `pattern`, `recursive` | Wildcard search (e.g. `*.py`, `*notes*`). Caps output at 500 files to protect memory. |
| **`list_directory`** | `directory`, `include_hidden` | Lists files and subfolders with types, readable sizes, and modification timestamps. |
| **`get_file_info`** | `path` | Detailed metadata: canonical path, file extension, size in bytes/readable units, created/modified dates. |
| **`read_text_file`** | `path`, `max_characters` | Safely reads text/code files (TXT, PY, JS, TS, HTML, CSS, JSON, MD, etc.). Capped at 10 MB with binary detection. |
| **`find_recent_files`**| `directory`, `days`, `recursive` | Finds files modified within the last N days, sorted newest first. |
| **`find_large_files`** | `directory`, `minimum_size_mb`, `recursive` | Finds large files exceeding a size threshold, sorted largest to smallest. |
| **`organize_files_preview`** | `directory` | Analyzes a folder and produces a categorized sorting preview without touching any files. |

---

### 3. Controlled Modification Tools & Verification

All file write tools require explicit user confirmation. Operations are audited and rigorously verified:

| Tool Name | Action | Verification Rule |
| :--- | :--- | :--- |
| **`copy_file`** | Copies file from source to destination. | Verifies destination exists and exact byte size matches source. |
| **`move_file`** | Relocates file from source to destination. | Verifies destination exists and source no longer exists on disk. |
| **`rename_file`** | Renames a file or folder in-place. | Verifies new file exists, old file is gone, and rejects path injection. |
| **`create_directory`** | Creates a new folder. | Verifies directory was created and is accessible. |
| **`organize_files`** | Moves files into typed subfolders. | Moves files into typed subfolders with automatic conflict prevention. |

---

### 4. Interactive Confirmation System

When the model invokes a file modification tool, `ToolExecutor` halts automated execution and emits a `confirmation_requested` signal. The Chat UI renders an interactive `ConfirmationCardWidget`:

```text
┌────────────────────────────────────────────────────────────┐
│ 🛡️ File Operation Approval Required                        │
│                                                            │
│ Action: Move File                                          │
│ Source: C:\Users\Downloads\quarterly_report.pdf            │
│ Destination: C:\Users\Documents\PDFs\quarterly_report.pdf   │
│ Risk: Source file will be relocated to destination.        │
│                                                            │
│                          [✕ Reject]   [✓ Approve & Execute]│
└────────────────────────────────────────────────────────────┘
```

- Clicking **`[✓ Approve & Execute]`**: Triggers `agent_core.execute_confirmed_tool()`, performs the operation with post-execution verification, updates the card to green (`✓ Operation completed and verified.`), and logs the audit record to SQLite.
- Clicking **`[✕ Reject]`**: Aborts the operation, updates the card to red (`✗ Operation rejected by user.`), and prevents any filesystem modification.

---

### 5. Smart File Organization Workflow

Personal Agent can organize cluttered directories (such as Downloads) automatically using standard file type categories:

1. **Documents**: PDF, DOC, DOCX, TXT, MD, PPT, PPTX, XLS, XLSX, CSV
2. **Images**: PNG, JPG, JPEG, GIF, BMP, WEBP, SVG
3. **Videos**: MP4, MKV, AVI, MOV, WMV
4. **Audio**: MP3, WAV, FLAC, AAC, OGG
5. **Archives**: ZIP, RAR, 7Z, TAR, GZ
6. **Installers**: EXE, MSI
7. **Code**: PY, JAVA, C, CPP, H, CS, JS, TS, HTML, CSS, JSON, SQL, SH, BAT, PS1
8. **Other**: Uncategorized files

**Preview-First Guarantee**: Calling `organize_files_preview` provides the proposed plan first. If approved via `organize_files`, typed subfolders are created and files are relocated without overwriting existing files.

---

## ⚡ Phase 2.2.1 — Agent Tool Engine

Phase 2.2.1 introduces an extensible, secure tool execution engine into Personal Agent. Instead of operating as a purely conversational model, the agent can now determine when real-world system data is required, validate tool invocations, execute approved Python functions, and summarize the results in clear natural language.

### 1. Tool Execution Architecture & Flow Diagram

All tool requests flow through a strict 5-stage safety pipeline:

```text
       User Request
            │
            ▼
        Agent Core
            │
            ▼
        Qwen 3 8B
            │
            ▼
      Tool Selection (Native Ollama API / Structured Fallback)
            │
            ▼
      Tool Validation (Schema, Required Args, Types, Unexpected Keys)
            │
            ▼
     Permission Check (Safe Read-Only vs Sensitive vs Destructive)
            │
            ▼
      Tool Execution (Isolated Handler, Start/Stop Timers, Error Catching)
            │
            ▼
       Tool Result (Structured JSON {success, tool, result, duration_ms})
            │
            ▼
        Qwen 3 8B (Interprets Tool Results in Round 2)
            │
            ▼
      Final Response (Clear Natural-Language Summary to User)
```

---

### 2. Tool Registry & Extensibility

The tool subsystem lives in `app/tools/` and consists of clean, decoupled components:
- **`app/tools/tool_registry.py`**: Manages `ToolDefinition` instances (name, description, parameter schemas in JSON Schema format, callable handler, permission level, and category). Exposes `get_ollama_tools()` to translate definitions into the standard OpenAI/Ollama function format.
- **`app/tools/tool_validator.py`**: Validates tool calls against schemas before execution. Rejects missing required parameters, invalid data types (e.g. string for integer, boolean for integer), and unexpected arguments.
- **`app/tools/tool_permissions.py`**: Enforces execution safety levels (`SAFE_READ_ONLY`, `SAFE_ACTION`, `SENSITIVE_READ`, `MODERATE_WRITE`, `DESTRUCTIVE`). Determines whether tools execute automatically or require future confirmation dialogs.
- **`app/tools/tool_executor.py`**: Coordinates validation, permission checks, execution isolation, and execution timing (`duration_ms`). Returns structured `ToolExecutionResult` objects and prevents tool exceptions from crashing the application.
- **`app/tools/built_in_tools.py`**: Implements the initial suite of safe, read-only system tools.

---

### 3. Available Built-in Tools

| Tool Name | Parameters | Description | Example Output |
| :--- | :--- | :--- | :--- |
| **`get_current_time`** | *None* | Returns the current local system date, time, and timestamp. | `{"result": "November 21, 2026, 01:27 PM"}` |
| **`get_system_info`** | *None* | Returns non-sensitive host computer info: OS, Windows version, computer name, CPU model, core count, RAM capacity, available RAM, and CPU usage. | `{"result": {"os": "Windows 11", "cpu": "Intel64 Family 6...", "ram_total": "31.7 GB", "ram_available": "10.0 GB", "cpu_usage": "20.5%"}}` |
| **`get_gpu_info`** | *None* | Queries `nvidia-smi` to return NVIDIA GPU model, utilization %, total VRAM, used VRAM, free VRAM, and GPU temperature. Safely handles missing drivers or non-NVIDIA environments. | `{"result": {"gpu_name": "NVIDIA GeForce RTX 3050 Laptop GPU", "gpu_utilization": "4%", "vram_total": "6144 MB", "vram_used": "5689 MB", "gpu_temperature": "59°C"}}` |

---

### 4. Permission System & Safety Policies

To prevent untrusted code execution or unauthorized access:
- **Execution Level Hierarchy**:
  - `SAFE_READ_ONLY`: Automated read-only queries (system time, specs, GPU stats). Always auto-approved.
  - `SAFE_ACTION`: Non-destructive actions (file reading, search).
  - `MODERATE_WRITE`: Modifying files, creating folders (requires user confirmation in future phases).
  - `DESTRUCTIVE`: Deleting files, killing processes, system alterations (strictly requires explicit user confirmation).
- **Hard Boundaries**:
  - Never executes arbitrary Python code generated by the LLM.
  - Never runs arbitrary terminal shell commands in this phase.
  - Tools must be explicitly registered in `ToolRegistry`; all unknown tools are immediately rejected.

---

### 5. Model Tool-Calling Mechanism & Structured Fallback

1. **Native Ollama Tool Calling**: Personal Agent uses Ollama's native `/api/chat` function-calling protocol by passing `tools: [...]` alongside user messages.
2. **Multi-Round Execution Loop**: `OllamaChatWorker` manages a loop with a **maximum limit of 5 rounds** per request to prevent infinite loops:
   - Round 1: Prompt + Tools passed to Ollama. Model emits reasoning `<think>` tokens and requests tool call(s).
   - Tool Execution: Tools are validated, permitted, executed, timed, and saved to SQLite.
   - Round 2: Tool outputs are appended as `role: "tool"` messages and fed back into Qwen 3 8B.
   - Final Answer: Model analyzes the output and streams the final natural-language response.
3. **Structured JSON Fallback**: If Ollama or an alternative model emits a structured tool call in text instead of the API parameter (e.g. `{"name": "...", "arguments": {}}`), `_check_structured_tool_fallback` automatically parses and executes it.

---

### 6. UI Integration & Indicators

- **Chat Activity Badges (`ToolActivityWidget`)**:
  - Displays a clean visual card inside the chat stream when a tool is called.
  - While running: `⚙ Running tool: Get System Info...` with an amber left border.
  - Upon completion: `✓ Tool: Get System Info — Retrieved successfully (166.0 ms)` with a subtle green border.
  - Upon error: `✗ Tool: ... — Failed: ...` with a subtle red border.
- **Agent Panel & Status Bar**:
  - Right Agent Panel updates execution state to `Using tool: Get System Info`.
  - Activity log registers tool events in real time.

---

### 7. SQLite Tool Execution Persistence

Stored in `data/agent_database.sqlite`:
```sql
CREATE TABLE IF NOT EXISTS tool_executions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id TEXT DEFAULT 'default',
    tool_name TEXT NOT NULL,
    arguments TEXT,
    result TEXT,
    status TEXT NOT NULL,
    duration_ms REAL DEFAULT 0.0,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🚀 Phase 2.1 — Local AI Integration & NVIDIA GPU Acceleration

### 1. Ollama Integration & Model Discovery
- **Native Local API**: Directly communicates with the local Ollama daemon at `http://localhost:11434` using native standard library HTTP requests (`/api/tags`, `/api/chat`, `/api/ps`).
- **Existing Model Detection**: Automatically queries installed models without re-downloading or reinstalling. Detects and auto-selects:
  ```text
  qwen3:8b (Tag ID: 500a1f067a9f, Size: 5.2 GB disk / 5.7 GB in memory)
  ```
- **Dynamic Model Switching**: Model selector dropdown in the Chat header with an instant refresh button (`↻`).

---

### 2. GPU Acceleration Diagnosis & Resolution

#### Hardware Profile
- **GPU**: NVIDIA GeForce RTX 3050 Laptop GPU (6,144 MiB / 6.0 GB VRAM)
- **CPU**: Intel Core i7-13650HX (14 cores, 20 threads)
- **RAM**: 32 GB DDR5
- **Driver**: 617.42 | **CUDA Runtime**: 13.4 / CUDA v12 Ollama runner

#### Root Cause Analysis for Previous CPU Fallback
1. Windows Desktop Window Manager (DWM) and active graphics applications reserve **~1,100–1,250 MiB** of VRAM at all times.
2. This leaves **~4,800–4,900 MiB** of allocatable VRAM.
3. Qwen 3 8B model weights require **~5.2 GB** in GGUF Q4 quantization.
4. When loaded with Ollama's default 32K or unconstrained context window, the combined weight memory and KV-cache exceeded free physical VRAM. Ollama automatically defaulted to 100% CPU inference to prevent driver crashes.

#### Implemented Optimization & Parameters
In `app/core/model_manager.py`, generation parameters were explicitly configured:
- `num_ctx: 4096` — Bounds the KV-cache to a stable, memory-efficient context window that comfortably fits in remaining VRAM.
- `num_gpu: -1` — Directs Ollama to offload the maximum possible layers to the GPU.
- `temperature: 0.7` — Balanced creativity and precision for desktop assistance.

#### Verified Live GPU Telemetry (`ollama ps` & `nvidia-smi`)
```text
C:\> ollama ps
NAME        ID              SIZE      PROCESSOR                UNTIL
qwen3:8b    500a1f067a9f    5.7 GB    70%/30% GPU/CPU          4m55s
```

- **Active Compute Process**: `PID 34520` (`ollama_llama_server.exe` using CUDA v12)
- **VRAM Dedicated to Ollama**: **4,218 MiB**
- **Inference Speed**: **18.3 – 20.4 tokens/second** (vs. ~2.1 tokens/s on CPU)
- **GPU Core Utilization**: **88% – 95%** during generation
- **Operating Temperature**: **54°C – 56°C** under continuous generation

---

## 🖥️ Application Layout & Pages

The application is structured into a persistent 3-part layout:

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│ [Logo] Personal Agent                  Header / Page Title                  [ ─ ] [ □ ] [ ✕ ]   │
├──────────────┬──────────────────────────────────────────────────────────────┬───────────────────┤
│ 🏠 Home      │                                                              │ 🤖 AGENT PANEL    │
│ 💬 Chat      │                                                              │ Status: Active    │
│ 📋 Tasks     │                                                              │ Model: qwen3:8b   │
│ 📁 Files     │                                                              │ Runner: llamacpp  │
│ 🌐 Browser   │                      MAIN WORKSPACE                          │ Offload: 70% GPU  │
│ 💻 Coding    │               (Switches between 11 pages)                    │                   │
│ ⚡ Workflows │                                                              │ Recent Activity:  │
│ 🎙️ Voice     │                                                              │ • Model loaded    │
│ 🧠 Memory    │                                                              │ • 🔧 get_time ok  │
│ 📜 History   │                                                              │                   │
│ ⚙️ Settings   │                                                              │                   │
├──────────────┴──────────────────────────────────────────────────────────────┴───────────────────┤
│ ● Ollama: Online (qwen3:8b)   |   CPU: 12.4%   |   RAM: 72.1%   |   GPU: 14% (5.4/6.0 GB)  | v2.2.2 │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Project Structure

```
PersonalAgent/
│
├── main.py                     # Application entry point with logging & high-DPI scaling
├── requirements.txt             # PySide6, psutil dependencies
│
├── app/
│   ├── ui/
│   │   ├── main_window.py       # Three-part window layout, status bar, and model listeners
│   │   ├── sidebar.py           # Left sidebar navigation with amber pill accent
│   │   ├── theme.qss            # Custom dark charcoal QSS stylesheet
│   │   │
│   │   ├── pages/               # 11 Modular workspace views
│   │   │   ├── home_page.py     # Command input, quick actions, active tasks
│   │   │   ├── chat_page.py     # Streaming chat UI, ToolActivityWidget, ConfirmationCardWidget
│   │   │   ├── tasks_page.py    # Metric counters, task queue, and creation dialog
│   │   │   ├── files_page.py    # Local file manager with Windows drive selector
│   │   │   ├── browser_page.py  # AI browser layout with controls & viewport
│   │   │   ├── coding_page.py   # VS Code-style IDE with Explorer, Editor, and Terminal
│   │   │   ├── workflows_page.py# Automation Builder with custom node canvas
│   │   │   ├── voice_page.py    # Voice assistant with visualizer and push-to-talk
│   │   │   ├── memory_page.py   # SQLite-backed persistent memory store
│   │   │   ├── history_page.py  # Activity history timeline with category filters
│   │   │   └── settings_page.py # Settings with Ollama test & GPU hardware status
│   │   │
│   │   └── panels/
│   │       ├── __init__.py
│   │       └── agent_panel.py   # Persistent right-side agent monitoring panel
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── agent.py             # AgentCore & OllamaChatWorker (multi-round loop & confirmation)
│   │   ├── model_manager.py     # ModelManager (Ollama API, model discovery, GPU query)
│   │   ├── task_manager.py      # SQLite task queue manager
│   │   └── system_monitor.py    # CPU, RAM, and NVIDIA GPU metrics monitor
│   │
│   ├── tools/                   # Extensible Tool Subsystem
│   │   ├── __init__.py          # Package initialization & tool registration
│   │   ├── tool_registry.py     # ToolRegistry & ToolDefinition schemas
│   │   ├── tool_validator.py    # ToolValidator schema and type enforcement
│   │   ├── tool_permissions.py  # ToolPermissionPolicy & PermissionLevel (includes ControlledAction & ProcessModification)
│   │   ├── tool_executor.py     # ToolExecutor with timing, confirmation & safety
│   │   ├── built_in_tools.py    # System tools: get_current_time, get_system_info, get_gpu_info
│   │   ├── filesystem_safety.py # FilesystemSafety: system folder blocking & traversal checks
│   │   ├── file_tools.py        # 12 file intelligence, modification & organization tools
│   │   ├── app_discovery.py     # Multi-source app discovery (App Paths, Start Menu, Uninstall, PATH) & resolver
│   │   ├── process_manager.py   # Safe psutil process inspection, status check & graceful termination
│   │   └── app_tools.py         # 9 application and process control tools
│   │
│   ├── automation/              # Staged for workflow automation
│   ├── memory/
│   │   └── memory_store.py      # SQLite memory querying and categorization
│   └── database/
│       └── db.py                # SQLite schema with messages, tasks, and tool_executions
│
├── data/                        # Persistent SQLite database (`agent_database.sqlite`)
├── logs/                        # Standard logging output (`personal_agent.log`)
├── tests/                       # Automated test suites (41 / 41 Tests Passing — 100%)
│   ├── test_app.py              # Phase 1 UI, navigation, and resize verification (6/6)
│   ├── test_phase2.py           # Phase 2.1 Ollama, streaming, GPU benchmark suite (5/5)
│   ├── test_phase2_2_1.py       # Phase 2.2.1 Tool registry, validator, executor, and agent loop (6/6)
│   ├── test_phase2_2_2.py       # Phase 2.2.2 Filesystem safety, file tools & organization (5/5)
│   ├── test_phase2_2_3.py       # Phase 2.2.3 App discovery, launch, process tools & safety (19/19)
│   └── screenshots/             # Rendered test screenshots matching UI reference
├── ui images/                   # Provided UI reference screenshots
└── README.md                    # Project documentation & progress report
```

---

## 🗄️ Database Schema

Stored in `data/agent_database.sqlite`:

```sql
-- Chat message history
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'user',
    content TEXT NOT NULL,
    model TEXT DEFAULT '',
    conversation_id TEXT DEFAULT 'default',
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tool execution audit log (Phase 2.2.1, 2.2.2 & 2.2.3)
CREATE TABLE IF NOT EXISTS tool_executions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id TEXT DEFAULT 'default',
    tool_name TEXT NOT NULL,
    arguments TEXT,
    result TEXT,
    status TEXT NOT NULL,
    duration_ms REAL DEFAULT 0.0,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Task management queue
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT DEFAULT 'general',
    status TEXT DEFAULT 'waiting',
    progress INTEGER DEFAULT 0,
    start_time TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Persistent memory store
CREATE TABLE IF NOT EXISTS memory_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Activity history log
CREATE TABLE IF NOT EXISTS activity_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL,
    description TEXT NOT NULL,
    status TEXT DEFAULT 'info',
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🚀 Getting Started & Installation

### Prerequisites
- **Python**: 3.12 or higher
- **Ollama**: Installed and running on `http://localhost:11434`
- **Model**: `qwen3:8b` pulled in Ollama:
  ```bash
  ollama list
  ```
- **NVIDIA GPU (Recommended)**: NVIDIA GPU with driver 535+ and CUDA support for hardware acceleration.

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/adisingh592/agent_pro.git
   cd agent_pro
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify Ollama is active**:
   ```bash
   ollama ps
   ```

5. **Launch Personal Agent**:
   ```bash
   python main.py
   ```

---

## 🧪 Verification & Benchmark Tests

### 1. Milestone C Desktop Actions & Coordinate Grounding Suite
```bash
python tests/test_milestone_c_desktop_actions.py
```
**Test Results (23 / 23 Tests Passed — 100%)**:
```text
Ran 23 tests in 0.006s — OK (100% Success Rate)
[1/23]  test_screen_metrics                     --> PASSED (Resolution, multi-monitor bounds, DPI scale)
[2/23]  test_normalized_to_actual_center        --> PASSED (Norm (500, 500) -> Actual (960, 540))
[3/23]  test_normalized_to_actual_corners       --> PASSED (Norm (0, 0) and (1000, 1000) mapped correctly)
[4/23]  test_actual_to_normalized               --> PASSED (Pixel (960, 540) -> Norm (500, 500))
[5/23]  test_out_of_bounds_rejection            --> PASSED (Rejected coordinates outside [0, 1000])
[6/23]  test_clamp_to_screen                    --> PASSED (Clamped coordinates to virtual display rect)
[7/23]  test_initial_state_inactive             --> PASSED (Emergency stop default inactive)
[8/23]  test_trigger_emergency_stop             --> PASSED (Latching circuit breaker and input release)
[9/23]  test_failsafe_corner_detection          --> PASSED (Corner slam (0,0) immediately triggers abort)
[10/23] test_reset_emergency_stop               --> PASSED (Deliberate reset restores readiness)
[11/23] test_move_mouse_normalized              --> PASSED (Normalized cursor positioning)
[12/23] test_click_mouse                        --> PASSED (Dispatched left, right, middle clicks)
[13/23] test_scroll_mouse                       --> PASSED (Vertical & horizontal scroll ticks)
[14/23] test_type_text                          --> PASSED (Simulated keyboard input without auto-Enter)
[15/23] test_press_safe_key                     --> PASSED (Approved safe keys and combinations)
[16/23] test_blocked_unapproved_key             --> PASSED (Unvalidated keys rejected KEY_NOT_ALLOWED)
[17/23] test_actions_blocked_during_stop        --> PASSED (All actions blocked during emergency stop)
[18/23] test_tools_registered                   --> PASSED (All 11 desktop action tools registered)
[19/23] test_screen_metrics_auto_approved       --> PASSED (Read-only display metrics auto-approved)
[20/23] test_emergency_stop_auto_approved       --> PASSED (Instant emergency stop trigger auto-approved)
[21/23] test_mutating_action_requires_confirm   --> PASSED (Mutating click stages for approval card)
[22/23] test_type_text_requires_confirmation    --> PASSED (Typing stages for approval card)
[23/23] test_confirmed_action_executes          --> PASSED (User-confirmed physical actions execute)
```

### 2. Phase 2.3 Windows UI Automation Engine Suite
```bash
python tests/test_phase2_3_windows_ui_automation.py
```
**Test Results (20 / 20 Tests Passed — 100%)**:
```text
Ran 20 tests in 0.002s — OK (100% Success Rate)
[1/20]  test_list_windows_returns_structured_data --> PASSED (Valid WindowInfo list)
[2/20]  test_list_windows_respects_max_results    --> PASSED (Limits results count)
[3/20]  test_get_active_window                    --> PASSED (Current foreground window)
[4/20]  test_find_window_nonexistent_returns_none --> PASSED (Graceful missing window handling)
[5/20]  test_inspect_window_nonexistent           --> PASSED (Graceful inspection failure)
[6/20]  test_compact_observation_generation      --> PASSED (Compact LLM tree format)
[7/20]  test_element_matching_logic_mocked        --> PASSED (Exact, substring, fuzzy, ambiguity)
[8/20]  test_find_element_in_nonexistent_window   --> PASSED (Proper error payload)
[9/20]  test_action_executor_disabled_protection  --> PASSED (Rejects clicking disabled controls)
[10/20] test_read_element_sensitive_masking       --> PASSED (Automatic password masking)
[11/20] test_controlled_action_requires_confirm   --> PASSED (Click/type staged for confirmation)
[12/20] test_safe_keys_recognized                 --> PASSED (Allowlist recognition)
[13/20] test_key_allowlist_enforcement            --> PASSED (Blocks unauthorized keys)
[14/20] test_phase2_3_tools_registered            --> PASSED (All 9 UI tools registered)
[15/20] test_read_only_tools_auto_approved        --> PASSED (Auto-approves read-only tools)
[16/20] test_list_windows_executor_execution      --> PASSED (Runs through ToolExecutor pipeline)
[17/20] test_get_active_window_executor_execution --> PASSED (Runs through ToolExecutor pipeline)
[18/20] test_click_ui_element_requires_confirm    --> PASSED (Staged ConfirmationCardWidget)
[19/20] test_press_key_requires_confirm           --> PASSED (Staged ConfirmationCardWidget)
[20/20] test_find_window_exact_and_substring      --> PASSED (Window title matching)
```

### 3. Phase 2.2.3 Application & Process Control Suite
```bash
python tests/test_phase2_2_3.py
```
**Test Results (19 / 19 Tests Passed — 100%)**:
```text
======================================================================
Ran 19 tests in 42.253s

OK
[1/19] test_caching_behavior                              --> PASSED (1-hour TTL cache hit & invalidation)
[2/19] test_exact_resolution                              --> PASSED (Exact 'Notepad' match, 1.0 confidence)
[3/19] test_alias_resolution                              --> PASSED ('vs code' -> 'Visual Studio Code', 'chrome' -> 'Google Chrome')
[4/19] test_fuzzy_resolution                              --> PASSED ('google chrom' -> 'Google Chrome' >0.65)
[5/19] test_ambiguous_resolution                          --> PASSED ('Visual Studio' returns candidate choices)
[6/19] test_unknown_application                           --> PASSED (Rejected non-existent app)
[7/19] test_launch_requires_confirmation                  --> PASSED (Staged ConfirmationCardWidget)
[8/19] test_launch_rejects_dangerous_shell_injection      --> PASSED (Blocked shell metacharacters '&', '|', ';', '$')
[9/19] test_launch_handles_invalid_application            --> PASSED (Safe error handling)
[10/19] test_open_file_requires_confirmation_and_validates --> PASSED (Enforced FilesystemSafety boundaries & confirmation)
[11/19] test_open_folder_requires_confirmation            --> PASSED (Validated folder & confirmation card)
[12/19] test_list_running_processes                       --> PASSED (Enumerated processes with memory MB, CPU %, PID)
[13/19] test_check_application_status                     --> PASSED (Active 'python' detected; fake app reported offline)
[14/19] test_get_process_info_by_pid                      --> PASSED (Retrieved exact PID stats & create time)
[15/19] test_critical_process_protection                  --> PASSED (Blocked termination of explorer.exe, svchost, System, agent PID)
[16/19] test_graceful_process_closure_on_dummy_subprocess --> PASSED (Graceful terminate() + exit verification on dummy subprocess)
[17/19] test_phase2_2_3_tools_registered                  --> PASSED (All 9 tools in registry with correct permission levels)
[18/19] test_search_applications_executor_execution       --> PASSED (Executed through ToolExecutor pipeline)
[19/19] test_list_running_processes_executor_execution    --> PASSED (Executed through ToolExecutor pipeline)
```

### 4. Phase 2.2.2 File Intelligence & Operations Suite
```bash
python tests/test_phase2_2_2.py
```
*(Verifies filesystem boundaries, search, read, copy, move, rename, directory creation, smart organization — 5/5 PASSED).*

### 5. Phase 2.2.1 Agent Tool Engine Suite
```bash
python tests/test_phase2_2_1.py
```
*(Verifies tool registration, JSON schema validation, permissions, 3 safe built-in tools, and live multi-round agent loop with Ollama `qwen3:8b` — 6/6 PASSED).*

### 6. Phase 2.1 Hardware & GPU Benchmark Suite
```bash
python tests/test_phase2.py
```
*(Verifies Ollama connectivity, `qwen3:8b` detection, RTX 3050 GPU monitoring, and 18.3–20.4 tokens/s streaming — 5/5 PASSED).*

### 7. Phase 1 UI & Regression Suite
```bash
python tests/test_app.py
```
*(Verifies all 11 pages, sidebar navigation, window resizing, and theme consistency — 6/6 PASSED).*

**TOTAL: 84 / 84 TESTS PASSING (100% SUCCESS RATE ACROSS ALL PHASES)**

---

## 🔮 Roadmap Ahead

- [x] **Phase 1: Desktop UI Foundation** (Complete)
- [x] **Phase 2.1: Local AI Integration & NVIDIA GPU Acceleration** (Complete)
- [x] **Phase 2.2.1: Agent Tool Engine** (Complete)
- [x] **Phase 2.2.2: File Intelligence & Safe File Operations** (Complete)
- [x] **Phase 2.2.3: Application & Process Control** (Complete)
- [x] **Milestone A: Architecture & Safety Specification** (Complete)
- [x] **Phase 2.3 / Milestone B: Windows UI Automation Engine** (Complete)
- [x] **Milestone C: Desktop Actions & Coordinate Grounding** (Complete)
- [ ] **Milestone D: Browser Automation Backend** (Next Staged)
  - Playwright / Chrome DevTools Protocol integration.
  - Semantic DOM locators, network idle synchronization, form automation.
- [ ] **Milestone E: Visual & OCR Fallback Engine**
  - Configurable lightweight VLM interface.
  - Windows Media OCR / Tesseract fallback for canvas/Direct3D apps.
- [ ] **Milestone F: Autonomous Task Execution Engine**
  - Observe-Ground-Act-Verify ReAct loop, dynamic TaskPlanner.
- [ ] **Milestone G: Safety, Scoping & Human Oversight**
  - Application scoping, dry-run simulation mode, emergency abort (`Ctrl+Alt+X`).
- [ ] **Milestone H: Skill Memory & Trajectory Replay**
  - Parameterized skill storage, zero-LLM fast-path replay.
- [ ] **Milestone I: Desktop UI Integration & End-to-End Testing**
  - Live execution cards, step-by-step progress drawer, abort button.
