# Reference Repository Architectural Analysis & Benchmark

This document provides a deep architectural comparative analysis of three prominent open-source computer-use and desktop automation repositories to inform the design of **Personal Agent's Unified Autonomous Computer Control Engine**:

1. **WindowsAgent** (`ibraheem-mustafa-dev/windowsagent`)
2. **UI-TARS Desktop** (`bytedance/UI-TARS-desktop`)
3. **AutoGUI** (`BillJr99/AutoGUI`)

---

## 📑 Summary Matrix

| Evaluation Dimension | WindowsAgent | UI-TARS Desktop (ByteDance) | AutoGUI (BillJr99) | Personal Agent Target Strategy |
| :--- | :--- | :--- | :--- | :--- |
| **Primary Interaction Paradigm** | Windows UI Automation (UIA) & Accessibility Tree | End-to-End Vision-Language Model (VLM) Pixel Actions | Hybrid: Accessibility Tree + Set-of-Mark (SoM) + Tools | **Hybrid 5-Level Architecture** (API → UIA → Browser DOM → Visual → OCR) |
| **Core Execution Loop** | Observe → Ground → Act → Verify | Think → Coordinate Prediction → OS Input → Screenshot | ReAct (Reason → Act → Observe) Tool Loop | **Bounded ReAct with State Verification & Grounding** |
| **Windows Desktop Support** | Windows-native (UIA + Win32 APIs) | Cross-platform via synthetic mouse/keyboard events | Cross-platform (Windows, macOS, Linux, WSL) | **Windows 11 Native** (UIA, Win32, canonical filesystem, process hooks) |
| **Browser Engine** | Chrome DevTools Protocol (CDP) / Playwright | Browser Operator (visual + DOM) | Headless/Headed Playwright Integration | **Playwright + CDP Accessibility Tree & DOM Locators** |
| **Visual Grounding** | Fallback screenshot inspection | Primary: UI-TARS Multimodal Model (bounding boxes) | Set-of-Mark (SoM) + OCR (Tesseract / EasyOCR) | **Configurable Vision Backend** (Decoupled from primary text LLM) |
| **Safety & Governance** | Hardcoded action restrictions | Approval dialogs & permission checks | Destructive command blacklist & approval countdowns | **4-Tier Permission Architecture** (Read-Only, Controlled, Approval, Restricted) |
| **Task Verification** | UI tree delta check & window state | Post-action screenshot comparison | Output assertion & return-code verification | **Deterministic Multi-State Verifier** (Process, window, DOM, file stats) |
| **Skills & Workflows** | Static application profiles | Model system prompts | Parameterized trajectory saving & replay | **Replayable Parameterized Skills in SQLite** |
| **Resource Overhead** | Low (Python UIA + HTTP client) | High (Requires dedicated 7B/72B VLM server) | Moderate (Python runtime + Playwright) | **Constrained (6GB VRAM, RTX 3050)**: Text Qwen3 8B + lightweight vision |
| **Open Source License** | MIT | Apache-2.0 | MIT | **Permissive Integration** (All clean-room or MIT/Apache-2.0 aligned) |

---

## 1. Deep Dive: WindowsAgent (`ibraheem-mustafa-dev/windowsagent`)

### 1.1 Architectural Overview
WindowsAgent is built specifically around the premise that **pixel-coordinate guessing is fundamentally brittle on desktop operating systems**. Desktop windows resize, scale under High-DPI settings, reorder z-indices, and alter themes. WindowsAgent focuses on structured semantic interaction through the **Microsoft Windows UI Automation (UIA)** framework.

### 1.2 Core Execution Loop: Observe → Ground → Act → Verify
```text
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   OBSERVE    │ ──> │    GROUND    │ ──> │     ACT      │ ──> │    VERIFY    │
│ Enumerate    │     │ Map Request  │     │ Invoke UIA   │     │ Confirm Tree │
│ UIA Tree     │     │ to Element   │     │ Pattern/Win32│     │ State Delta  │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
```
1. **Observe**: Enumerates top-level desktop windows, identifies the active focused window, and extracts a filtered, flattened representation of its accessibility tree (ControlTypes, AutomationIDs, Names, BoundingRectangles, and Supported Patterns).
2. **Ground**: Compares the user's natural-language goal (e.g. *"Click the Save button"*) against candidate elements in the active window hierarchy. Disambiguates based on element type, hierarchy path, and enabled status.
3. **Act**: Invokes the appropriate native UIA pattern (`InvokePattern`, `ValuePattern.SetValue`, `SelectionItemPattern.Select`) rather than blindly firing synthetic mouse clicks at screen coordinates.
4. **Verify**: Queries the target window or element post-action to confirm that the expected state change occurred (e.g. dialog closed, text updated, checkbox toggled).

### 1.3 Key Strengths Worth Adapting
- **Accessibility-First Interaction**: Interacting directly through UIA patterns avoids screen resolution mismatches, multi-monitor coordinate offsets, and occluded window issues.
- **Application Profiles**: Maintains lightweight application metadata profiles describing common window layouts, hotkeys, and menu paths for standard Windows applications (e.g., File Explorer, Notepad, Settings).
- **Graceful Error Recovery**: When an element cannot be found in the current UIA tree, the agent attempts window re-focusing, parent navigation, or visual fallback before failing.

### 1.4 Limitations & Anti-Patterns to Avoid
- **Incomplete Browser Support**: Treating browser windows as generic UIA controls results in sluggish, deeply nested accessibility trees. Browsers must be automated via structured DOM/CDP protocols.
- **Tight Coupling to Specific Cloud LLMs**: Hardcoded prompt schemas designed exclusively for proprietary APIs.

---

## 2. Deep Dive: UI-TARS Desktop (`bytedance/UI-TARS-desktop`)

### 2.1 Architectural Overview
UI-TARS Desktop is an enterprise-grade multimodal GUI agent developed by ByteDance. It treats the graphical interface as a pure visual canvas, relying on a specialized **Vision-Language Model (VLM)** trained specifically for GUI understanding and coordinate grounding.

```text
       User Prompt + Screen Capture
                   │
                   ▼
       Vision-Language Model (VLM)
      ("Think" trace + Coordinate output)
                   │
                   ▼
     Normalized Coordinates: [x, y]
                   │
                   ▼
       Display Coordinate Scaler
       (DPI & Screen Dimension Scaling)
                   │
                   ▼
            Operating System
         (Mouse & Keyboard Driver)
```

### 2.2 Key Subsystems
1. **Agent Runtime (`@tarko/agent`)**: Manages the outer perception-action loop, maintaining execution context and multi-turn action histories.
2. **Model Provider Layer (`@tarko/model-provider`)**: Standardizes multimodal requests, streaming visual thinking tokens (`<thought>...</thought>`), and parsing action formats (e.g. `click(x=452, y=318)`, `type(text="hello")`, `hotkey(keys=["ctrl", "s"])`).
3. **Operator Engine**: Drives synthetic input events (mouse movement, clicks, drag-and-drop, scroll wheel, keystrokes) across local and remote desktop environments.
4. **MCP Tool Integration**: Incorporates the Model Context Protocol (MCP) to bridge visual actions with external tools and services.

### 2.3 Key Strengths Worth Adapting
- **Universal Visual Fallback**: When an application custom-renders its interface via Direct3D, OpenGL, Vulkan, or Canvas (e.g. games, Blender, video editors, legacy controls with zero accessibility nodes), visual grounding provides the only viable path to interaction.
- **Normalized Coordinate System**: Maps visual coordinates to a `[0, 1000]` normalized scale, decoupled from physical screen resolutions, before translating to physical pixels via display scaling math.
- **Detailed Action Tracing**: Generates structured before-and-after visual diffs for every executed step, enabling auditability and failure analysis.

### 2.4 Limitations & Anti-Patterns for Personal Agent
- **VRAM Incompatibility**: UI-TARS requires dedicated multimodal model weights (7B, 13B, or 72B parameter vision models). Attempting to co-host a heavy vision model alongside our active `qwen3:8b` model on a **6GB RTX 3050 GPU** would immediately exhaust VRAM and trigger severe swap thrashing.
- **Lack of Semantic Understanding**: A purely visual model cannot inspect clipboard text, read off-screen DOM content, verify background process completion, or inspect file hashes directly.

---

## 3. Deep Dive: AutoGUI (`BillJr99/AutoGUI`)

### 3.1 Architectural Overview
AutoGUI is an open-source, model-agnostic desktop automation agent. It establishes a multi-tool **ReAct loop** where an LLM is provided with structured tools spanning the terminal, filesystem, browser, and desktop GUI.

```text
                       ReAct Agent Execution Loop
 ┌────────────────────────────────────────────────────────────────────────┐
 │                                                                        │
 │  1. OBSERVATION: Capture Screen / Accessibility / Shell Output         │
 │  2. REASONING:   Analyze State & Formulate Step Hypothesis             │
 │  3. ACTION:      Select & Validate Registered Tool Call                │
 │  4. GUARDRAIL:   Safety Policy Check & Destructive Command Guard       │
 │  5. EXECUTION:   Run Tool & Measure Duration                           │
 │  6. POST-CHECK:  Verify Observable Outcome                             │
 │                                                                        │
 └────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Key Subsystems & Innovations
1. **ReAct Planner**: Guides the agent to alternate between reasoning traces and concrete tool invocations, breaking compound requests into manageable sub-goals.
2. **Hybrid Grounding (Accessibility + Set-of-Mark + OCR)**:
   - Primary: Accessibility tree element matching.
   - Secondary: Set-of-Mark (SoM) overlays numbering visual targets for vision models.
   - Tertiary: OCR extraction for unlabelled visual text.
3. **Playwright Integration**: Launches isolated headless or headed browser contexts, locating web elements via standard CSS, XPath, and accessibility text locators.
4. **Safety & Permission Guardrails**:
   - Destructive command pattern matching (blocking `format`, `rm -rf`, `del /f /s`, `drop database`).
   - Approval countdowns giving users a cancellation window before sensitive operations.
5. **Skill Persistence**: Enables storing successful action trajectories as reusable, parameterized skills that can be replayed with new inputs.

### 3.3 Key Strengths Worth Adapting
- **Multi-Level Interaction Hierarchy**: Seamlessly blends shell commands, file tools, browser DOM actions, and GUI clicks into a cohesive tool registry.
- **Safety Guardrails**: Proactive inspection of tool arguments for dangerous patterns before passing them to the execution layer.
- **Playwright DOM Engine**: Reliable web automation that bypasses desktop accessibility bottlenecks.
- **Skill Storage & Trajectory Replay**: Capturing validated multi-step workflows into persistent storage for reliable reuse.

---

## 4. Synthesis & Architectural Strategy for Personal Agent

### 4.1 The 5-Level Interaction Priority Hierarchy
Personal Agent will neither rely purely on pixel clicking (UI-TARS) nor restrict itself exclusively to accessibility nodes (WindowsAgent). Instead, it adopts a **strict 5-level interaction hierarchy**:

```text
LEVEL 1: Structured APIs & System Tools (Fastest, 100% deterministic, 0 vision cost)
   │     Examples: file_tools, process_tools, app_launcher, CLI utilities.
   ▼
LEVEL 2: Windows UI Automation (Semantic desktop interaction, high reliability)
   │     Examples: UIA button invoke, menu select, text box setValue, window focus.
   ▼
LEVEL 3: Browser Structured DOM via Playwright (Web interaction, rich locators)
   │     Examples: page.click(text=...), page.fill(selector=...), navigation, tabs.
   ▼
LEVEL 4: Visual Grounding (Complementary fallback for canvas/custom GUI)
   │     Examples: Normalized coordinate click, icon match, visual diff.
   ▼
LEVEL 5: OCR Fallback (Text extraction on unlabelled graphics)
         Examples: Windows native OCR, text bounding box location.
```

### 4.2 Resource Budgeting Strategy for RTX 3050 (6GB VRAM)
- **Primary Text Engine**: `qwen3:8b` via Ollama (`num_ctx: 4096`, 70% GPU offload, ~4,200 MiB VRAM).
- **Visual Engine**: Decoupled. Do not load heavy VLM models into local GPU VRAM simultaneously.
  - Option A: Native Windows UIA + fast local Tesseract/Windows native OCR (0 MiB VRAM).
  - Option B: Lightweight vision models (e.g. MobileVLM, Qwen2-VL-2B on CPU or lightweight quantization) only when Level 4 visual grounding is explicitly triggered.
  - Option C: Configurable external multimodal endpoint if requested by user.

### 4.3 Component Mapping into Personal Agent

| Architectural Need | Inspired By | Target Personal Agent Subsystem |
| :--- | :--- | :--- |
| **UIA Tree & Patterns** | WindowsAgent | `app/automation/backends/windows_uia.py` |
| **Observation & Grounding** | WindowsAgent + AutoGUI | `app/automation/observation_engine.py`, `grounding_engine.py` |
| **Browser DOM Engine** | AutoGUI | `app/automation/backends/browser_backend.py` (Playwright) |
| **Visual Operator & Scaler** | UI-TARS Desktop | `app/automation/backends/visual_backend.py`, `windows_input.py` |
| **ReAct Task Planner** | AutoGUI | `app/automation/task_planner.py`, `execution_engine.py` |
| **Deterministic Verifier** | WindowsAgent | `app/automation/verification_engine.py` |
| **Action Guardrails & Scoping**| AutoGUI + WindowsAgent | `app/automation/safety/action_validator.py`, `approval_manager.py` |
| **Persistent Skills & Replay** | AutoGUI | `app/automation/action_history.py`, SQLite `skills` table |
| **User Interface & Approvals** | Existing Personal Agent | `app/ui/pages/chat_page.py`, `ConfirmationCardWidget` |

---

## 5. Licensing & Reuse Considerations

- **WindowsAgent**: MIT License. Safe for clean-room architectural pattern adaptation.
- **UI-TARS Desktop**: Apache-2.0 License. Permissive; code ideas and operator interfaces can be adapted provided Apache-2.0 attribution notices are preserved where applicable.
- **AutoGUI**: MIT License. Highly permissive; tool structures and ReAct loop designs can be adapted directly.
- **Personal Agent Clean-Room Architecture**: All code will be developed natively in Python 3.12+ and PySide6, ensuring strict independence, zero licensing friction, and complete alignment with the existing project structure.
