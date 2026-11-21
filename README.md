# Personal Agent — Desktop AI Assistant

A high-performance personal desktop AI assistant built with **Python 3.12+**, **PySide6**, and an **SQLite-ready modular architecture**, powered by **local Ollama LLMs with NVIDIA GPU hardware acceleration** and a **safe, extensible tool-calling execution engine**.

Inspired by VS Code, Antigravity, and modern developer workspaces, Personal Agent provides a centralized, professional command center designed for speed, visual clarity, and future autonomous desktop capabilities.

---

## 📌 Project Status: Phase 2.2.1 (Complete & Verified)

> **Current Milestone**: Phase 2.2.1 — Agent Tool Engine  
> **Target Hardware**: NVIDIA GeForce RTX 3050 Laptop GPU (6GB VRAM) / Intel Core i7-13650HX / 32GB RAM / Windows 11  
> **Model**: `qwen3:8b` (5.2 GB GGUF, Q4_K_M) via Ollama (`llamacpp` CUDA v12 runner)  
> **Repository**: [https://github.com/adisingh592/agent_pro.git](https://github.com/adisingh592/agent_pro.git)  

---

## 📑 Table of Contents

1. [Features Overview](#-features-overview)
2. [Phase 2.2.1 — Agent Tool Engine](#-phase-221--agent-tool-engine)
   - [Tool Execution Architecture & Flow Diagram](#1-tool-execution-architecture--flow-diagram)
   - [Tool Registry & Extensibility](#2-tool-registry--extensibility)
   - [Available Built-in Tools](#3-available-built-in-tools)
   - [Permission System & Safety Policies](#4-permission-system--safety-policies)
   - [Model Tool-Calling Mechanism & Fallback](#5-model-tool-calling-mechanism--structured-fallback)
   - [UI Integration & Indicators](#6-ui-integration--indicators)
   - [SQLite Tool Execution Persistence](#7-sqlite-tool-execution-persistence)
3. [Phase 2.1 — Local AI Integration & NVIDIA GPU Acceleration](#-phase-21--local-ai-integration--nvidia-gpu-acceleration)
4. [Application Layout & Pages](#-application-layout--pages)
5. [Project Structure](#-project-structure)
6. [Database Schema](#-database-schema)
7. [Getting Started & Installation](#-getting-started--installation)
8. [Verification & Benchmark Tests](#-verification--benchmark-tests)
9. [Roadmap Ahead](#-roadmap-ahead)

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
| **Instant Interruption** | Responsive "Stop Generating" (`⏹`) control that cancels network socket operations and tool execution immediately. | ✅ Complete |
| **Persistent Storage** | SQLite-backed database storing tasks, memories, activity history, chat messages, and tool executions. | ✅ Complete |
| **Live Hardware Monitor** | Background polling of CPU %, RAM %, GPU utilization %, VRAM allocation, and GPU temperature. | ✅ Complete |

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
│ ● Ollama: Online (qwen3:8b)   |   CPU: 12.4%   |   RAM: 72.1%   |   GPU: 14% (5.4/6.0 GB)  | v2.2.1 │
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
│   │   │   ├── chat_page.py     # Streaming chat UI, ToolActivityWidget, model selector
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
│   │   ├── agent.py             # AgentCore & OllamaChatWorker (multi-round tool execution loop)
│   │   ├── model_manager.py     # ModelManager (Ollama API, model discovery, GPU query)
│   │   ├── task_manager.py      # SQLite task queue manager
│   │   └── system_monitor.py    # CPU, RAM, and NVIDIA GPU metrics monitor
│   │
│   ├── tools/                   # Phase 2.2.1 Agent Tool Engine
│   │   ├── __init__.py          # Tool package initialization & auto-registration
│   │   ├── tool_registry.py     # ToolRegistry & ToolDefinition schemas
│   │   ├── tool_validator.py    # ToolValidator schema and type enforcement
│   │   ├── tool_permissions.py  # ToolPermissionPolicy & PermissionLevel
│   │   ├── tool_executor.py     # ToolExecutor with timing, containment, and safety
│   │   └── built_in_tools.py    # Safe tools: get_current_time, get_system_info, get_gpu_info
│   │
│   ├── automation/              # Staged for workflow automation
│   ├── memory/
│   │   └── memory_store.py      # SQLite memory querying and categorization
│   └── database/
│       └── db.py                # SQLite schema with messages, tasks, and tool_executions
│
├── data/                        # Persistent SQLite database (`agent_database.sqlite`)
├── logs/                        # Standard logging output (`personal_agent.log`)
├── tests/                       # Automated test suites
│   ├── test_app.py              # Phase 1 UI, navigation, and resize verification
│   ├── test_phase2.py           # Phase 2.1 Ollama, streaming, GPU benchmark suite
│   ├── test_phase2_2_1.py       # Phase 2.2.1 Tool registry, validator, executor, and agent loop
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

-- Tool execution audit log (Phase 2.2.1)
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

### 1. Phase 2.2.1 Agent Tool Engine Suite
```bash
python tests/test_phase2_2_1.py
```
**Test Results**:
```text
========================================================
 ALL PHASE 2.2.1 TESTS PASSED SUCCESSFULLY! (6/6)       
========================================================
[1/6] Testing Tool Registration...       --> PASSED (Registration, retrieval & Ollama format)
[2/6] Testing Tool Validation...         --> PASSED (Required keys, types & unexpected params)
[3/6] Testing Built-in Tools Execution.. --> PASSED (time: 0.05ms, sys: 166ms, gpu: 57ms)
[4/6] Testing Tool Permissions...        --> PASSED (Safe read auto-approved, destructive rejected)
[5/6] Testing SQLite Tool History...     --> PASSED (Logged to tool_executions table)
[6/6] Testing Live Agent Tool Loop...    --> PASSED (Qwen 3 called get_current_time, formulated answer)
```

### 2. Phase 2.1 Hardware & GPU Benchmark Suite
```bash
python tests/test_phase2.py
```
*(Verifies Ollama connectivity, `qwen3:8b` detection, RTX 3050 GPU monitoring, and 18.3–20.4 tokens/s streaming).*

### 3. Phase 1 UI & Regression Suite
```bash
python tests/test_app.py
```
*(Verifies all 11 pages, sidebar navigation, window resizing, and theme consistency without headless display crashes).*

---

## 🔮 Roadmap Ahead

- **Phase 2.2.2: Safe File Operations & File Management Tools**
  - Read files, search files, move files, copy files, rename files, create directories.
  - User confirmation dialogs for write operations.
- **Phase 2.2.3: Application Management & System Automation**
  - Launch applications, detect running processes, graceful process termination.
- **Phase 3: Coding IDE & Automation Engine**
  - Monaco Editor / QScintilla code editor integration with syntax highlighting.
  - Node-based workflow execution from the Automation Builder.
- **Phase 4: Multimodal Voice & Autonomous Agents**
  - Offline local Whisper speech-to-text and Piper TTS voice feedback.
