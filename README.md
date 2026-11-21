# Personal Agent — Desktop AI Assistant

A high-performance personal desktop AI assistant built with **Python 3.12+**, **PySide6**, and an **SQLite-ready modular architecture**, powered by **local Ollama LLMs with NVIDIA GPU hardware acceleration**.

Inspired by VS Code, Antigravity, and modern developer workspaces, Personal Agent provides a centralized, professional command center designed for speed, visual clarity, and future autonomous system capabilities.

---

## 📌 Project Status: Phase 2.1 (Complete & Verified)

> **Current Milestone**: Phase 2.1 — Local AI Integration, Ollama & NVIDIA GPU Acceleration  
> **Hardware Target**: NVIDIA GeForce RTX 3050 Laptop GPU (6GB VRAM) / Intel Core i7-13650HX / 32GB RAM  
> **Status**: Successfully integrated with existing local Ollama installation, verified GPU offloading with `qwen3:8b`, and enabled non-blocking token streaming.

---

## 🚀 Phase 2.1 — Local AI Integration & NVIDIA GPU Acceleration

### 1. Ollama Integration & Model Discovery
- **Local API Integration**: Directly connects to the local Ollama service at `http://localhost:11434` via native HTTP APIs (`/api/tags`, `/api/chat`, `/api/ps`).
- **Existing Model Detection**: Automatically queries installed models without re-downloading or reinstalling. Detects and auto-selects the installed model:
  ```text
  qwen3:8b (Size: 5.2 GB on disk, 5.7 - 6.0 GB in memory)
  ```
- **Model Switching**: Dynamic model selector dropdown in the Chat page and Settings with instant refresh (↻).

---

### 2. GPU Acceleration Diagnosis & Resolution

#### Hardware Environment
- **GPU**: NVIDIA GeForce RTX 3050 6GB Laptop GPU
- **VRAM Total**: 6,144 MiB (~6.0 GB)
- **Driver**: 617.42 | **CUDA UMD**: 13.4
- **Host System RAM**: 32 GB | **CPU**: Intel Core i7-13650HX

#### Diagnosis of Previous CPU-Only Execution
1. **Windows Desktop VRAM Overhead**: In normal Windows operation, desktop compositor and active desktop applications (Edge, Windows Terminal, IDEs) consume ~1.2 GB of VRAM.
2. **Context Window Sizing**: The default context window for Qwen 3 (up to 32,768 tokens) allocates significant KV cache memory in VRAM. When context window was unconstrained, the total memory required exceeded available VRAM (4.9 GB free), triggering Ollama to fail GPU allocation and fall back to 100% CPU.
3. **The Solution**:
   - Explicitly configured `num_ctx: 4096` as the optimal default context size (with a 2048 low-VRAM option).
   - Configured `num_gpu: -1` to force Ollama to maximize GPU layer offloading.
   - At `num_ctx: 4096`: Ollama successfully offloads **70% of layers to the RTX 3050 GPU** and 30% to high-speed system RAM.
   - At `num_ctx: 2048`: Ollama offloads **75% of layers to the GPU**.

#### Verified GPU Offload Metrics (`ollama ps` & `nvidia-smi`)
- **Active Processor**: `30%/70% CPU/GPU` (llamacpp runner)
- **VRAM Allocated**: **5,385 MiB / 6,144 MiB**
- **Inference Speed**: **18.3 - 20.4 tokens/second**
- **GPU Temperature**: 52°C - 56°C under load

---

### 3. Non-Blocking Real-Time Chat Streaming
- **UI Responsiveness (QThread Worker)**: All Ollama HTTP communications execute inside `OllamaChatWorker` on a dedicated background thread. The PySide6 UI event loop never locks, stutters, or freezes during inference.
- **Progressive Streaming**: Tokens appear incrementally in the UI as generated.
- **Reasoning & Content Support**: Supports both Qwen 3 thinking mode (`thinking` token chunks wrapped in `<think>...</think>`) and direct text generation.
- **Stop Generation**: The chat Send button transforms into an active Stop button (⏹) during generation, cleanly aborting the stream via socket closure without hanging.
- **Clear Conversation**: Allows clearing in-memory context and SQLite history with a single click.

---

### 4. Persistent Chat History & SQLite Storage
- Chat messages persist across application restarts in `data/agent_database.sqlite`.
- Message schema tracks `id`, `sender` ("You" / "Agent"), `role` ("user" / "assistant"), `content`, `model` (`qwen3:8b`), `conversation_id`, and `timestamp`.
- Past messages automatically hydrate into multi-turn conversation memory on application launch.

---

### 5. System Prompt & Agent Persona
Personal Agent is configured with a system prompt that:
- Acts as a concise, practical local desktop AI assistant.
- Assists with computer tasks, coding analysis, file organization, and workflow structure.
- Asks clarifying questions when user instructions are ambiguous.
- Clearly distinguishes between planning a task and executing a task.
- Strictly refrains from falsely claiming to have executed actions, changed files, or launched external software before those capabilities are active in later phases.

---

### 6. Live GPU & System Resource Monitoring
- `SystemMonitor` queries CPU and RAM via `psutil`, and NVIDIA GPU utilization, VRAM usage, and temperature via `nvidia-smi` queries.
- Bottom Status Bar displays live metrics:
  ```text
  CPU: 14.5% | RAM: 73.2% | GPU: 12% (5.4/6.0 GB) | Phase 2.1
  ```
- Gracefully handles environments without NVIDIA GPUs without crashing.

---

## 🛠️ Project Structure

```
PersonalAgent/
│
├── main.py                     # Application entry point with logging & high-DPI
├── requirements.txt             # PySide6 & psutil dependencies
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
├── tests/                       # Automated UI verification suite
│   ├── test_app.py              # Phase 1 UI, navigation, and resize verification
│   ├── test_phase2.py           # Phase 2.1 Ollama, streaming, GPU benchmark suite
│   └── screenshots/             # Rendered test screenshots matching UI reference
├── ui images/                   # Provided UI reference screenshots
└── README.md                    # Project documentation & progress report
```

---

## 🧪 Verification & Benchmark Tests

All automated tests have been verified:

### Run Phase 2.1 Verification Suite
```bash
python tests/test_phase2.py
```

**Benchmark Results**:
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

### Run Phase 1 Compatibility Suite
```bash
python tests/test_app.py
```
*(Verifies that all 11 pages navigate without errors, window resizing works, and visual themes remain intact).*

---

## 🚀 How to Run

### 1. Ensure Ollama Is Running
```bash
ollama serve
```

### 2. Run Personal Agent
```bash
python main.py
```

---

## 🔮 Roadmap Ahead

- **Phase 2.2: Tool Execution & Computer Control**
  - Tool calling protocol with Qwen 3 function calling format.
  - Safe file tools: file search, folder organization, automated download manager.
  - Safe command execution in sandbox mode.
- **Phase 3: Coding IDE & Automation Engine**
  - Monaco Editor / QScintilla code editor integration.
  - Node-based workflow execution from the Automation Builder.
- **Phase 4: Multimodal Voice & Autonomous Agents**
  - Local Whisper speech-to-text and Piper TTS voice feedback.
  - Autonomous multi-step desktop workflows.
