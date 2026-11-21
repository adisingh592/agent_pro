# Personal Agent — Desktop AI Assistant

A high-performance personal desktop AI assistant built with **Python 3.12+**, **PySide6**, and an **SQLite-ready modular architecture**, powered by **local Ollama LLMs with NVIDIA GPU hardware acceleration**.

Inspired by VS Code, Antigravity, and modern developer workspaces, Personal Agent provides a centralized, professional command center designed for speed, visual clarity, and future autonomous system capabilities.

---

## 📌 Project Status: Phase 2.1 (Complete & Verified)

> **Current Milestone**: Phase 2.1 — Local AI Integration, Ollama & NVIDIA GPU Acceleration  
> **Target Hardware**: NVIDIA GeForce RTX 3050 Laptop GPU (6GB VRAM) / Intel Core i7-13650HX / 32GB RAM / Windows 11  
> **Model**: `qwen3:8b` (5.2 GB GGUF, Q4_K_M) running via Ollama (`llamacpp` CUDA v12 runner)  
> **Repository**: [https://github.com/adisingh592/agent_pro.git](https://github.com/adisingh592/agent_pro.git)  

---

## 📑 Table of Contents

1. [Features Overview](#-features-overview)
2. [Phase 2.1 — Local AI Integration & NVIDIA GPU Acceleration](#-phase-21--local-ai-integration--nvidia-gpu-acceleration)
   - [Ollama Integration & Discovery](#1-ollama-integration--model-discovery)
   - [GPU Acceleration Root Cause & Fix](#2-gpu-acceleration-diagnosis--resolution)
   - [Non-Blocking Real-Time Streaming](#3-non-blocking-real-time-chat-streaming)
   - [SQLite Chat History Persistence](#4-persistent-chat-history--sqlite-storage)
   - [System Prompt & Assistant Persona](#5-system-prompt--agent-persona)
   - [Hardware & Resource Monitoring](#6-live-gpu--system-resource-monitoring)
3. [Application Layout & Pages](#-application-layout--pages)
4. [Project Structure](#-project-structure)
5. [Database Schema](#-database-schema)
6. [Getting Started & Installation](#-getting-started--installation)
7. [Verification & Benchmark Tests](#-verification--benchmark-tests)
8. [Roadmap Ahead](#-roadmap-ahead)

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
| **Instant Interruption** | Responsive "Stop Generating" (`⏹`) control that cancels network socket operations immediately. | ✅ Complete |
| **Persistent Storage** | SQLite-backed database storing tasks, memories, activity history, and multi-turn chat messages. | ✅ Complete |
| **Live Hardware Monitor** | Background polling of CPU %, RAM %, GPU utilization %, VRAM allocation, and GPU temperature. | ✅ Complete |
| **Tool Calling & Execution** | Structured function execution (filesystem, process management, shell commands). | ⏳ Phase 2.2 |

---

## 🚀 Phase 2.1 — Local AI Integration & NVIDIA GPU Acceleration

### 1. Ollama Integration & Model Discovery
- **Native Local API**: Directly communicates with the local Ollama daemon at `http://localhost:11434` using native standard library HTTP requests (`/api/tags`, `/api/chat`, `/api/ps`).
- **Zero Redownload Enforcement**: Automatically discovers existing models on disk. Connects directly to the installed model:
  ```text
  qwen3:8b (Tag ID: 500a1f067a9f, Size: 5.2 GB disk / 5.7 GB in memory)
  ```
- **Dynamic Model Switching**: Model selector dropdown in the Chat header with an instant refresh button (`↻`) to pick from any locally installed Ollama models.

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

```text
+-----------------------------------------------------------------------------------------+
| NVIDIA-SMI 617.42                 Driver Version: 617.42         CUDA Version: 13.4     |
|-----------------------------------+------------------------+----------------------------+
| GPU  Name            TCC/WDDM     | Bus-Id          Disp.A | Volatile Uncorr. ECC       |
| Fan  Temp   Perf     Pwr:Usage/Cap|           Memory-Usage | GPU-Util  Compute M.       |
|===================================+========================+============================|
|   0  NVIDIA GeForce ...     WDDM  |   00000000:01:00.0  On |                        N/A |
| N/A   54C    P0         42W /  60W|    5385MiB /   6144MiB |     94%      Default       |
+-----------------------------------+------------------------+----------------------------+
| Processes:                                                                              |
|  GPU   GI   CI              PID   Type   Process name                        GPU Memory |
|=========================================================================================|
|    0   N/A  N/A           34520      C   ...runners\cuda_v12\ollama_llama_...    4218MiB|
+-----------------------------------------------------------------------------------------+
```

- **Active Compute Process**: `PID 34520` (`ollama_llama_server.exe` using CUDA v12)
- **VRAM Dedicated to Ollama**: **4,218 MiB**
- **Inference Speed**: **18.3 – 20.4 tokens/second** (vs. ~2.1 tokens/s on CPU)
- **GPU Core Utilization**: **88% – 95%** during generation
- **Operating Temperature**: **54°C – 56°C** under continuous generation

---

### 3. Non-Blocking Real-Time Chat Streaming
- **UI Responsiveness (`QThread` Worker)**: All HTTP communication with Ollama executes inside `OllamaChatWorker` on a separate thread. The main Qt event loop remains at 60 FPS; UI elements never freeze or drop inputs.
- **Dual Token Streaming**: Supports both Qwen 3 reasoning/thinking tokens (`chunk["message"]["thinking"]` formatted inside collapsible `<think>...</think>` containers) and primary content tokens (`chunk["message"]["content"]`).
- **Instant Interruption**: Clicking the Stop button (`⏹`) immediately triggers `stop_generation()`, terminating the socket connection and resetting the UI state in < 50ms.
- **Clear Conversation**: Dedicated action (`🗑`) clears both the visible thread and the underlying SQLite message history.

---

### 4. Persistent Chat History & SQLite Storage
- All messages automatically save to `data/agent_database.sqlite`.
- Retains sender, role, content, model identifier, and timestamp.
- On launch or page navigation, past messages are automatically retrieved and rendered.

---

### 5. System Prompt & Agent Persona
Configured with an intelligent system instruction that:
- Acts as a knowledgeable, concise personal desktop assistant.
- Assists with technical development, file management, and planning.
- Asks clarifying questions when user instructions are ambiguous.
- Clearly states what actions are currently staged vs. executed, preventing simulated hallucinations.

---

### 6. Live GPU & System Resource Monitoring
- `SystemMonitor` polls CPU and RAM via `psutil`, and queries GPU status using lightweight `nvidia-smi` subprocess calls.
- Bottom Status Bar displays live metrics:
  ```text
  CPU: 14.5% | RAM: 73.2% | GPU: 12% (5.4/6.0 GB) | Phase 2.1
  ```
- Gracefully handles systems without NVIDIA hardware without crashing.

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
│ 🧠 Memory    │                                                              │ • Chat stream ok  │
│ 📜 History   │                                                              │                   │
│ ⚙️ Settings   │                                                              │                   │
├──────────────┴──────────────────────────────────────────────────────────────┴───────────────────┤
│ ● Ollama: Online (qwen3:8b)   |   CPU: 12.4%   |   RAM: 72.1%   |   GPU: 14% (5.4/6.0 GB)  | v2.1   │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### The 11 Modular Pages:
1. **Home**: Command bar, quick action shortcuts, active task summary, system stats.
2. **Agent Chat**: Live token streaming, model selection, reasoning toggle, stop/clear actions.
3. **Tasks**: Task queue, status filters (Running, Waiting, Completed), creation modal.
4. **Files**: Windows drive picker (C:, H:), folder navigation, file details table.
5. **Browser**: Staged UI browser workspace with URL bar and automation status.
6. **Coding Workspace**: VS Code-inspired IDE with Project Tree, Tabbed Editor, and Terminal.
7. **Workflows**: Visual node-based automation canvas for multi-step agent recipes.
8. **Voice Assistant**: Visual audio wave simulator and push-to-talk interface.
9. **Memory**: Categorized key-value persistent storage for agent knowledge.
10. **History**: Comprehensive timeline of user prompts, agent actions, and tool runs.
11. **Settings**: Connection test utility, context size slider, GPU acceleration diagnostics.

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
│   │   │   ├── chat_page.py     # Streaming chat UI, model selector, stop & clear buttons
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
│   │   ├── agent.py             # AgentCore & OllamaChatWorker (non-blocking streaming)
│   │   ├── model_manager.py     # ModelManager (Ollama API, model discovery, GPU query)
│   │   ├── task_manager.py      # SQLite task queue manager
│   │   └── system_monitor.py    # CPU, RAM, and NVIDIA GPU metrics monitor
│   │
│   ├── tools/                   # Staged for Phase 2.2 tool execution
│   ├── automation/              # Staged for workflow automation
│   ├── memory/
│   │   └── memory_store.py      # SQLite memory querying and categorization
│   └── database/
│       └── db.py                # SQLite schema with persistent messages & tasks
│
├── data/                        # Persistent SQLite database (`agent_database.sqlite`)
├── logs/                        # Standard logging output (`personal_agent.log`)
├── tests/                       # Automated test suites
│   ├── test_app.py              # Phase 1 UI, navigation, and resize verification
│   ├── test_phase2.py           # Phase 2.1 Ollama, streaming, GPU benchmark suite
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

-- Task management queue
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'pending',
    progress INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Persistent memory store
CREATE TABLE IF NOT EXISTS memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL,
    key TEXT NOT NULL,
    value TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Activity history log
CREATE TABLE IF NOT EXISTS history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action TEXT NOT NULL,
    details TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
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

### 1. Phase 2.1 Verification Suite (Hardware & Inference)
```bash
python tests/test_phase2.py
```
**Test Results**:
```text
========================================================
 ALL PHASE 2.1 VERIFICATION & GPU TESTS PASSED (5/5)!   
========================================================
[Step 1/5] Testing ModelManager & Ollama Connectivity...  --> PASSED (qwen3:8b detected)
[Step 2/5] Testing NVIDIA GPU Detection & Hardware...    --> PASSED (RTX 3050 6GB, 5.4GB VRAM)
[Step 3/5] Testing Real Streaming Inference...           --> PASSED (18.3 - 20.4 tokens/s)
[Step 4/5] Checking Ollama Processor Offloading...       --> PASSED (70% GPU offload, llamacpp)
[Step 5/5] Testing SQLite Chat History & Stop Mechanism...--> PASSED (Saved & Stopped cleanly)
```

### 2. Phase 1 UI & Regression Suite
```bash
python tests/test_app.py
```
*(Verifies all 11 pages, sidebar navigation, window resizing, and theme consistency without headless display crashes).*

---

## 🔮 Roadmap Ahead

- **Phase 2.2: Tool Execution & Computer Control**
  - Native JSON schema tool calling protocol for Qwen 3.
  - Safe file system tools: search, copy, move, and directory indexing.
  - Application launcher: launch, monitor, and close Windows applications.
  - Sandboxed command line runner with permission-level safety prompts.
- **Phase 3: Coding IDE & Automation Engine**
  - Monaco Editor / QScintilla integration with syntax highlighting and auto-completion.
  - Node-based workflow execution from the Automation Builder.
- **Phase 4: Multimodal Voice & Autonomous Agents**
  - Offline local Whisper speech-to-text and Piper TTS voice feedback.
  - Autonomous multi-step desktop workflows.
