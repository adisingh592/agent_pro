# Computer Automation Architecture Specification

This document details the architectural blueprint for **Personal Agent's Unified Autonomous Computer Control Engine**. It integrates structured system tools, Windows UI Automation (UIA), Playwright browser control, visual grounding, deterministic verification, and persistent skill memory into a cohesive, secure desktop system.

---

## 1. High-Level System Architecture

```text
                                 ┌────────────────────────┐
                                 │       USER INPUT       │
                                 └───────────┬────────────┘
                                             │
                                             ▼
                                 ┌────────────────────────┐
                                 │   PERSONAL AGENT UI    │
                                 │   (PySide6 / Desktop)  │
                                 └───────────┬────────────┘
                                             │
                                             ▼
                                 ┌────────────────────────┐
                                 │    LOCAL AI MODEL      │
                                 │ (Ollama / Qwen 3 8B)   │
                                 └───────────┬────────────┘
                                             │
                                             ▼
                                 ┌────────────────────────┐
                                 │   TASK UNDERSTANDING   │
                                 │   & Intent Extractor   │
                                 └───────────┬────────────┘
                                             │
                                             ▼
                                 ┌────────────────────────┐
                                 │      TASK PLANNER      │
                                 │ (Multi-Step DAG Plan)  │
                                 └───────────┬────────────┘
                                             │
                                             ▼
                                 ┌────────────────────────┐
                                 │ EXECUTION ORCHESTRATOR │
                                 │    (ReAct Loop)        │
                                 └───────────┬────────────┘
                                             │
               ┌─────────────────────────────┼─────────────────────────────┐
               ▼                             ▼                             ▼
    ┌─────────────────────┐       ┌─────────────────────┐       ┌─────────────────────┐
    │   WINDOWS ENGINE    │       │   BROWSER ENGINE    │       │    FILES ENGINE     │
    │  (UIA / Win32 Input)│       │(Playwright DOM/CDP) │       │ (Safe Path Guard)   │
    └──────────┬──────────┘       └──────────┬──────────┘       └──────────┬──────────┘
               │                             │                             │
               └─────────────────────────────┼─────────────────────────────┘
                                             │
                                             ▼
                                 ┌────────────────────────┐
                                 │   OBSERVATION ENGINE   │
                                 │(UIA Tree / DOM / Visual│
                                 └───────────┬────────────┘
                                             │
                                             ▼
                                 ┌────────────────────────┐
                                 │  VERIFICATION ENGINE   │
                                 │(Deterministic Outcome) │
                                 └───────────┬────────────┘
                                             │
                                             ▼
                                 ┌────────────────────────┐
                                 │    MEMORY & SKILLS     │
                                 │ (SQLite Persistent DAG)│
                                 └───────────┬────────────┘
                                             │
                                             ▼
                                 ┌────────────────────────┐
                                 │  FINAL USER RESPONSE   │
                                 └────────────────────────┘
```

---

## 2. The 5-Level Interaction Priority Hierarchy

To guarantee maximum speed, deterministic safety, and minimal resource consumption, Personal Agent enforces a **tiered execution preference**:

```text
 ┌────────────────────────────────────────────────────────────────────────┐
 │ LEVEL 1: APPLICATION & SYSTEM APIs                                    │
 │ Highest reliability, zero visual latency, 100% deterministic.         │
 │ • File read/write/move/copy (file_tools.py)                            │
 │ • Application discovery & launch (app_tools.py)                        │
 │ • Process status, inspection & close (process_manager.py)              │
 ├────────────────────────────────────────────────────────────────────────┤
 │ LEVEL 2: WINDOWS UI ACCESSIBILITY (UIA)                                │
 │ Native Windows control hierarchy, immune to screen resolution & DPI.   │
 │ • Enumerate active top-level and child windows                         │
 │ • Inspect ControlType (Button, Edit, Menu, TreeItem, TabItem)          │
 │ • Invoke standard UIA patterns (Invoke, Value, Toggle, Selection)     │
 │ • Synthetic input (mouse click, keyboard shortcut) to verified bounds  │
 ├────────────────────────────────────────────────────────────────────────┤
 │ LEVEL 3: STRUCTURED BROWSER ENGINE (PLAYWRIGHT)                        │
 │ Full DOM semantics, decoupled from desktop window clutter.             │
 │ • Semantic web locators (get_by_role, get_by_label, get_by_text)       │
 │ • Form filling, tab management, scroll, download handling              │
 │ • Direct DOM text extraction & page state monitoring                   │
 ├────────────────────────────────────────────────────────────────────────┤
 │ LEVEL 4: VISUAL GROUNDING (COMPLEMENTARY FALLBACK)                     │
 │ Applied when interfaces do not expose accessibility or DOM nodes.      │
 │ • Direct3D, OpenGL, Vulkan, and canvas-rendered interfaces             │
 │ • Normalized [0, 1000] coordinate target prediction                    │
 │ • Pre-and-post action screenshot comparison & diffing                  │
 ├────────────────────────────────────────────────────────────────────────┤
 │ LEVEL 5: OCR TEXT EXTRACTION FALLBACK                                  │
 │ Applied when unlabelled buttons or graphics contain visible text.      │
 │ • Native Windows OCR / Tesseract bounding box detection                │
 │ • Text cluster centroid targeting                                     │
 └────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Subsystem Package Layout: `app/automation/`

```text
app/
├── automation/
│   ├── __init__.py                # Automation package exports & unified manager
│   ├── automation_manager.py      # Facade coordinating planner, orchestrator, and backends
│   ├── task_planner.py            # Converts compound user requests into structured Step plans
│   ├── execution_engine.py        # Bounded ReAct loop with cancellation and stall guards
│   ├── observation_engine.py      # Captures multi-modal system state (UIA, DOM, Process, Screen)
│   ├── grounding_engine.py        # Resolves high-level actions to specific UIA nodes or DOM selectors
│   ├── verification_engine.py     # Deterministic post-action outcome verification
│   ├── action_history.py          # Trajectory recorder, audit trail, and skill packager
│   │
│   ├── backends/                  # Driver implementations for each automation tier
│   │   ├── __init__.py
│   │   ├── windows_uia.py         # Microsoft UI Automation tree walker & pattern invoker
│   │   ├── windows_input.py       # Win32 synthetic mouse and keyboard event injector
│   │   ├── browser_backend.py     # Playwright headless/headed browser session manager
│   │   └── visual_backend.py      # High-DPI screenshot capture & coordinate scaler
│   │
│   ├── models/                    # Typed dataclasses for agent state
│   │   ├── __init__.py
│   │   ├── action.py              # ActionCommand, ActionType, TargetElement, InputParameters
│   │   ├── observation.py         # DesktopObservation, UIAElementNode, DOMElementNode
│   │   └── task.py                # TaskPlan, TaskStep, ExecutionState, StepResult
│   │
│   └── safety/                    # Action scoping, validation, and approval rules
│       ├── __init__.py
│       ├── action_validator.py    # Pattern matching for destructive operations & injection
│       ├── approval_manager.py    # Interacts with chat ConfirmationCardWidget
│       └── application_scope.py   # Application whitelist, blacklisted folders, and boundaries
```

---

## 4. Core Data Models

### 4.1 Observation Model (`models/observation.py`)
```python
@dataclass
class UIAElementNode:
    name: str
    control_type: str             # "Button", "Edit", "MenuItem", "CheckBox", etc.
    automation_id: str
    class_name: str
    bounding_box: Tuple[int, int, int, int]  # (left, top, width, height)
    is_enabled: bool
    is_visible: bool
    supported_patterns: List[str] # ["InvokePattern", "ValuePattern", "SelectionItemPattern"]
    runtime_id: Optional[str] = None

@dataclass
class DesktopObservation:
    timestamp: float
    active_process_name: str
    active_window_title: str
    active_window_handle: int
    screen_resolution: Tuple[int, int]
    dpi_scale_factor: float
    visible_elements: List[UIAElementNode] = field(default_factory=list)
    screenshot_path: Optional[str] = None
    browser_url: Optional[str] = None
    browser_page_title: Optional[str] = None
```

### 4.2 Action Model (`models/action.py`)
```python
class ActionType(str, Enum):
    # Level 1: System / Tool
    TOOL_CALL = "tool_call"
    # Level 2: Windows UIA
    UIA_INVOKE = "uia_invoke"
    UIA_SET_VALUE = "uia_set_value"
    UIA_SELECT = "uia_select"
    # Level 3: Browser DOM
    BROWSER_NAVIGATE = "browser_navigate"
    BROWSER_CLICK = "browser_click"
    BROWSER_FILL = "browser_fill"
    # Level 4: Synthetic Input
    MOUSE_CLICK = "mouse_click"
    KEYBOARD_TYPE = "keyboard_type"
    KEYBOARD_HOTKEY = "keyboard_hotkey"
    MOUSE_SCROLL = "mouse_scroll"
    # Workflow
    WAIT_FOR_STATE = "wait_for_state"
    COMPLETE = "complete"

@dataclass
class ActionCommand:
    action_type: ActionType
    target_selector: Optional[str] = None       # Name, AutomationID, or CSS selector
    target_coordinates: Optional[Tuple[int, int]] = None
    input_text: Optional[str] = None
    hotkey_combo: Optional[List[str]] = None
    tool_name: Optional[str] = None
    tool_arguments: Optional[Dict[str, Any]] = None
    timeout_seconds: float = 10.0
    requires_approval: bool = False
    expected_outcome: Optional[str] = None
```

### 4.3 Task Plan Model (`models/task.py`)
```python
class ExecutionStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    AWAITING_APPROVAL = "awaiting_approval"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"

@dataclass
class TaskStep:
    step_id: int
    description: str
    action: ActionCommand
    status: ExecutionStatus = ExecutionStatus.PENDING
    start_time: Optional[float] = None
    completion_time: Optional[float] = None
    result_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    verification_passed: bool = False
    retry_count: int = 0

@dataclass
class TaskPlan:
    task_id: str
    goal_description: str
    steps: List[TaskStep]
    status: ExecutionStatus = ExecutionStatus.PENDING
    created_at: float = field(default_factory=time.time)
    max_steps: int = 25
    dry_run: bool = False
```

---

## 5. Bounded ReAct Execution Loop

The `ExecutionEngine` governs step-by-step dispatching with rigorous safeguards against runaways, infinite loops, and unverified successes:

```text
       Start Task
           │
           ▼
   Plan Validated? ──(No)──> Request Replanning / Report Error
           │ (Yes)
           ▼
┌──────────────────────────────────────────────┐
│  For Step in Plan:                           │
│                                              │
│  1. Check Cancellation & Max Time Bounds     │
│  2. Observe Current System State             │
│  3. Validate Preconditions & Safety Policy   │
│  4. Requires Approval? ──(Yes)──> Prompt User│
│                                   Wait Signal│
│  5. Execute Action via Preferred Backend     │
│  6. Observe New State                        │
│  7. Verify Outcome (VerificationEngine)      │
│     ├── Verified Success ──> Next Step       │
│     └── Verification Failed ──>              │
│         Can Recover? ──(Yes)──> Re-ground /  │
│                                 Retry Step   │
│                      ──(No)───> Abort Task   │
└──────────────────────────────────────────────┘
           │
           ▼
     Report Summary to User
```

### Loop Invariants & Safety Constraints
1. **Hard Step Cap**: Tasks cannot exceed 25 steps without explicit user permission.
2. **Iteration Timeout**: Single actions timeout after 10 seconds; overall tasks timeout after 300 seconds (5 minutes).
3. **No Phantom Successes**: A step is only marked `COMPLETED` when `VerificationEngine` explicitly confirms the post-action state delta.
4. **Stall Detection**: If three consecutive actions fail to alter the observed system state, execution pauses immediately with status `NEEDS_USER_INPUT`.

---

## 6. Hardware Budgeting & Resource Model (RTX 3050 6GB)

Personal Agent is strictly optimized for the target hardware profile:
- **GPU**: NVIDIA GeForce RTX 3050 Laptop GPU (6,144 MiB VRAM).
- **CPU**: Intel Core i7-13650HX (14 cores, 20 threads).
- **RAM**: 32 GB DDR5.

### VRAM & Processor Allocation Matrix
```text
┌────────────────────────────────────────────────────────────────────────┐
│ Total VRAM: 6,144 MiB                                                  │
│                                                                        │
│ ┌──────────────────────────────────────┐ ┌──────────┐ ┌──────────────┐ │
│ │ Qwen 3 8B (Q4_K_M GGUF via Ollama)   │ │ Windows  │ │ Safety VRAM  │ │
│ │ 70% GPU Offload (num_ctx: 4096)      │ │ Desktop  │ │ Headroom     │ │
│ │ ~4,218 MiB VRAM                      │ │ DWM & UI │ │              │ │
│ │                                      │ │ ~800 MiB │ │ ~1,126 MiB   │ │
│ └──────────────────────────────────────┘ └──────────┘ └──────────────┘ │
└────────────────────────────────────────────────────────────────────────┘
```

1. **Text Reasoning & Planning**: Handled locally by `qwen3:8b`.
2. **Windows UIA & Win32 Operations**: CPU-driven via Python `ctypes` / COM (0 MiB VRAM impact).
3. **Browser Engine**: Playwright Chromium running in background (0 MiB dedicated GPU VRAM).
4. **Vision Engine (When Level 4 is Active)**:
   - Uses lightweight visual processing (OpenCV template matching, native Windows OCR, or CPU-quantized vision encoders).
   - Never loads a second heavy VLM into GPU VRAM while Qwen 3 8B is loaded.
   - If a heavy external vision model is selected by the user, it communicates over HTTP API or runs on CPU threads.
