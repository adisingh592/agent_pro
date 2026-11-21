# PERSONAL AGENT — COMPREHENSIVE SAFETY & CONTROL ARCHITECTURE
**Document Version:** 1.0.0  
**Phase:** Computer Automation Engine (Milestone A)  
**Target Environment:** Windows 11 Desktop (NVIDIA RTX 3050 6GB / Intel Core i7-13650HX / 32GB RAM)

---

## 1. Executive Summary

Autonomous computer control grants an artificial intelligence agent the capability to interact directly with the operating system, file system, network, and graphical user interfaces. While this enables high-productivity workflows (e.g., automated document processing, complex system configurations, multi-app coordination), it introduces substantial risks:
- Accidental data loss or corruption (e.g., closing unsaved documents, deleting critical files).
- Unintended privilege escalation or system instability (e.g., terminating critical Windows services).
- Unauthorized exposure or transmission of sensitive user data (e.g., credential leakage, clipboard inspection).
- Runaway agent loops executing unbounded input sequences.

This document formalizes the **Personal Agent Safety & Control Architecture**. It synthesizes battle-tested safety patterns from `AutoGUI` (action scoping, dry-run mode, confirmation countdowns), `WindowsAgent` (process boundaries, UI validation), and enterprise agent guardrails into a robust, deterministic safety framework designed specifically for local Windows desktop execution.

---

## 2. Four-Tier Action Classification Taxonomy

Every atomic action dispatched by the Personal Agent must pass through the `SafetyEnforcer` and be classified into one of four rigid security tiers prior to execution:

```
+-------------------------------------------------------------------------------+
|                             INCOMING ACTION COMMAND                           |
|                      (tool, action_type, target, params)                      |
+---------------------------------------+---------------------------------------+
                                        |
                                        v
                          +---------------------------+
                          |   SafetyEnforcer Policy   |
                          +-------------+-------------+
                                        |
       +-----------------+--------------+---------------+-------------------+
       |                 |                              |                   |
       v                 v                              v                   v
+---------------+ +---------------+             +---------------+   +---------------+
|    TIER 1:    | |    TIER 2:    |             |    TIER 3:    |   |    TIER 4:    |
|   READ_ONLY   | |  CONTROLLED   |             |   APPROVAL    |   |  RESTRICTED   |
|               | |               |             |   REQUIRED    |   |  (FORBIDDEN)  |
+-------+-------+ +-------+-------+             +-------+-------+   +-------+-------+
        |                 |                             |                   |
        | Safe to execute | Within active scope         | Destructive/risky | STRICTLY      |
        | with 0 friction | & rate limits               | or external       | BLOCKED       |
        v                 v                             v                   v
+---------------+ +---------------+             +---------------+   +---------------+
| Auto-Execute  | | Auto-Execute  |             | Stage Action  |   | HARD REJECT   |
| Immediately   | | + Audit Log   |             | in Chat UI    |   | + Alert User  |
+---------------+ +---------------+             +-------+-------+   +---------------+
                                                        |
                                                +-------+-------+
                                                | User Decision |
                                                +-------+-------+
                                                | Approve -> Run
                                                | Reject  -> Cancel
```

### Tier 1: `READ_ONLY` (Zero-Friction Autonomous Observation)
- **Definition:** Non-mutating observation actions that cannot alter operating system state, modify user files, or communicate with external networks.
- **Permission Level:** Automatically permitted without user prompts.
- **Allowed Operations:**
  - Capturing desktop/window screenshots (`capture_screen`, `capture_window`).
  - Inspecting Windows UI Automation element trees (`inspect_ui_tree`, `get_focused_element`).
  - Reading public system telemetry (CPU, RAM, GPU, VRAM, battery).
  - Listing running processes (`list_processes`, `get_process_status`).
  - Reading existing files within permitted workspace/document directories (`read_file`, `list_directory`, `search_files`).
  - Inspecting window titles, bounding rectangles, and display DPI settings.

### Tier 2: `CONTROLLED` (Bounded Low-Risk State Mutations)
- **Definition:** Reversible or low-impact mutations directed at non-sensitive targets within the agent's active application scope.
- **Permission Level:** Permitted automatically **if and only if** target passes the `ScopeValidator` policy and rate limits.
- **Allowed Operations:**
  - Focusing an existing application window (`focus_window`, `bring_to_front`).
  - Minimizing or restoring application windows.
  - Clicking buttons or controls within an explicitly whitelisted application (e.g., clicking "Next" in a wizard).
  - Typing non-sensitive alphanumeric strings into verified text controls.
  - Launching standard non-elevated user applications (`launch_application` for Notepad, Calculator, VS Code, Edge).
  - Creating directories or writing temporary files within designated sandbox/workspace directories.
  - Scrolling a document or web page view.

### Tier 3: `APPROVAL_REQUIRED` (Interactive User Confirmation Card)
- **Definition:** Potentially destructive, irreversible, privacy-impacting, or security-sensitive actions that require human-in-the-loop validation.
- **Permission Level:** **Never auto-executed.** The action is staged into a visual confirmation card in the chat UI. Execution halts until the user clicks **Approve** or **Reject**.
- **Mandatory Approval Operations:**
  - Closing applications with potentially unsaved user data (`close_process`, `kill_application`).
  - Overwriting, moving, renaming, or deleting existing files outside temporary scratch folders.
  - Executing terminal commands or PowerShell scripts (`run_terminal_command`).
  - Submitting web forms (clicking "Submit", "Pay", "Confirm", "Buy", "Delete").
  - Entering text that resembles credentials, passwords, API tokens, or credit card numbers.
  - Launching processes with command-line arguments containing network URLs or file paths outside the workspace.
  - Interacting with administrative or system dialogs (UAC, Windows Settings, Network Adapters).

### Tier 4: `RESTRICTED` (Hard-Blocked Invariants)
- **Definition:** Operations deemed fundamentally hazardous to system integrity, security, or privacy.
- **Permission Level:** **Permanently forbidden.** Cannot be authorized even if the user attempts to grant permission via chat.
- **Prohibited Operations:**
  - Modifying the Windows Registry (`reg.exe`, `winreg` write operations).
  - Accessing or modifying `C:\Windows\System32`, `C:\Windows\SysWOW64`, or recovery partitions.
  - Accessing password managers, browser credential stores (e.g., `Login Data`), or cryptocurrency wallets.
  - Terminating critical Windows operating system processes (`csrss.exe`, `wininit.exe`, `services.exe`, `lsass.exe`, `smss.exe`, `explorer.exe`).
  - Disabling Windows Defender, Windows Firewall, or antivirus endpoint software.
  - Formatting drives or executing disk-partitioning tools (`diskpart`, `format`).
  - Modifying network interface routing tables or installing untrusted root certificates.

---

## 3. Action Scoping Architecture

To prevent the agent from wandering into unintended windows or modifying unrelated files, all actions must be bounded by explicit **Action Scopes**.

```
+---------------------------------------------------------------------------------+
|                                ACTION SCOPE MATRIX                              |
+---------------------------------------------------------------------------------+
|  APPLICATION SCOPE       |  FILESYSTEM SCOPE          |  NETWORK / BROWSER SCOPE|
+--------------------------+----------------------------+-------------------------+
| Allowed:                 | Allowed:                   | Allowed:                |
| - Notepad, Word, Excel   | - Active Workspace Folder  | - Localhost (127.0.0.1) |
| - VS Code, Git           | - H:\pro agent\scratch     | - User-whitelisted domains|
| - User-authorized web app| - User Documents / Projects| - Safe documentation sites|
|                          |                            |                         |
| Disallowed / Blacklisted:| Disallowed / Blacklisted:  | Disallowed:             |
| - Windows Settings / UAC | - C:\Windows\*             | - Financial portals     |
| - Registry Editor        | - C:\Program Files\* (del) | - Auth/OAuth endpoints  |
| - Password Managers      | - User AppData\Local\Vault | - Direct raw IP traffic |
| - PowerShell (Elevated)  | - Recycle Bin / Sys Volume | - Cloud credential APIs |
+--------------------------+----------------------------+-------------------------+
```

### 3.1 Application Window Scoping (`WindowGuard`)
Before dispatching any UI Automation click, keypress, or mouse movement, `WindowGuard` verifies the target window:
1. **Target Handle Validation:** Obtains the `HWND` and process ID (`PID`) of the foreground window.
2. **Process Identity Check:** Compares the PID against the designated task target process. If the user instructed the agent to edit a document in Notepad, but an unexpected pop-up or notification steals focus, the agent **pauses immediately** and will not dispatch keystrokes into the unverified window.
3. **Blacklisted Windows:** Windows belonging to `Taskmgr.exe`, `regedit.exe`, `mmc.exe`, `cmd.exe` (elevated), or security utilities are strictly inaccessible to synthetic mouse and keyboard input.

### 3.2 Filesystem Path Boundary (`PathGuard`)
Extending Phase 2.2.2's `FileSecurityManager`:
- Path normalization and traversal guards (`..` resolution, symlink checking).
- Read-only protection on root operating system drives (`C:\`).
- Workspace confinement: All file creation and intermediate outputs default strictly to the workspace scratch directory (`H:\pro agent\scratch\` or user-specified project roots).

---

## 4. Dry-Run & Simulation Engine

Before executing complex multi-step workflows, Personal Agent provides a **Dry-Run Mode** (`SimulationEngine`).

### 4.1 Dry-Run Mechanics
1. **Plan Generation:** The LLM decomposes the user request into an ordered sequence of `ActionCommand` objects.
2. **Virtual Execution:**
   - The engine steps through each action without calling OS APIs (no PyAutoGUI, no SendInput, no UI Automation pattern execution).
   - Locates UI elements in read-only mode to verify whether target buttons, text fields, or menu items exist on screen.
   - Filesystem mutations are checked against permissions without altering disk blocks.
3. **Simulation Report:** The agent presents an interactive summary in the chat:
   - Total planned steps.
   - Identified UI elements and target windows.
   - Predicted files created, modified, or moved.
   - Actions requiring explicit user approval (Tier 3).
   - Estimated execution time.
4. **User Confirmation:** The user can review the simulated trajectory and click **"Proceed with Live Execution"** or **"Abort/Modify"**.

---

## 5. Emergency Abort & Failsafe Architecture

Autonomous computer control must be instantly interruptible by the human operator at any millisecond of execution.

```
+-------------------------------------------------------------------------------+
|                       EMERGENCY FAILSAFE INPUT CHANNELS                       |
+-------------------------------------------------------------------------------+
|   Global Hotkey        Mouse Corner Slam       UI Cancel Button     Watchdog  |
|  [Ctrl + Alt + X]     (Cursor -> (0,0))       [Stop / Abort]       [Timeout]  |
+---------+--------------------+-----------------------+-------------------+----+
          |                    |                       |                   |
          +--------------------+-----------+-----------+-------------------+
                                           |
                                           v
                        +-------------------------------------+
                        |     EMERGENCY ABORT CONTROLLER      |
                        +------------------+------------------+
                                           |
                     +---------------------+---------------------+
                     |                                           |
                     v                                           v
       +----------------------------+              +----------------------------+
       |   HARDWARE INPUT CUTOFF    |              |     WORKER THREAD HALT     |
       | - Release all held keys    |              | - Stop QThread worker loop |
       | - Release mouse buttons    |              | - Clear task queue         |
       | - Unhook mouse/kb hooks    |              | - Set execution state IDLE |
       +----------------------------+              +----------------------------+
                     |                                           |
                     +---------------------+---------------------+
                                           |
                                           v
                        +-------------------------------------+
                        |          UI & SYSTEM RESTORE        |
                        | - Show desktop notification banner  |
                        | - Append "ABORTED BY USER" to chat  |
                        | - Log abort incident to SQLite audit|
                        +-------------------------------------+
```

### 5.1 Failsafe Trigger Mechanisms
1. **Physical Mouse Corner Slam (PyAutoGUI Failsafe):**
   - If the user physically yanks the mouse into any extreme screen corner (e.g., `(0, 0)`), the failsafe triggers within < 50ms.
2. **Dedicated Global Hotkey:**
   - A low-level keyboard hook listens for `Ctrl + Alt + X` or repeated `Escape` (pressed 3 times consecutively) even when Personal Agent is in the background.
3. **Prominent UI Abort Button:**
   - The `Stop` button in the UI remains active and elevated in the PySide6 event loop on the main thread while worker execution runs in a background `QThread`.
4. **Execution Watchdogs:**
   - **Per-Action Timeout:** Max 10 seconds per atomic action (prevents waiting indefinitely for a missing UI element).
   - **Total Task Timeout:** Max 300 seconds (5 minutes) for a complete autonomous task.
   - **Stall Guard:** If 3 consecutive actions produce identical screen states without progress, the agent pauses and asks for human assistance.

### 5.2 Abort Procedure & State Cleanup
When an abort is triggered:
1. `SafetyEnforcer` dispatches Windows API `SendInput` events to release any synthetic `KeyUp` or `MouseUp` events that might be held down.
2. The current action is cancelled; no further actions in the queue are popped.
3. The desktop cursor is returned to normal user control.
4. An immediate audit event is committed to the local database: `status: "ABORTED_BY_USER"`.
5. The chat interface displays an amber alert: *"⚠️ Task halted immediately by user intervention."*

---

## 6. Interactive Approval UI Specification

High-risk actions (Tier 3) must never be hidden behind generic modal dialogs. They are presented as dedicated **Staged Action Cards** within the Chat Stream.

### 6.1 Card Design & Data Contract
- **Header:** Risk badge (`🛡️ ACTION APPROVAL REQUIRED`) with amber color styling (`#FFB800` border, dark charcoal `#221C14` background).
- **Target Application:** Executable name, PID, and window title.
- **Action Details:** Specific method (`Launch`, `Close`, `Write File`, `Click Button`) and human-readable explanation.
- **Diff / Parameter Inspector:** Formatted table or code block showing parameters, file paths, or text payloads.
- **Interactive Controls:**
  - `[ Approve Action ]` (Solid amber button) — dispatches execution and resumes agent ReAct loop.
  - `[ Reject / Skip ]` (Ghost gray button) — cancels the specific action and informs LLM of user rejection.
  - `[ Abort Entire Task ]` (Red outline button) — stops the entire plan.
- **Auto-Reject Countdown (Optional):** Configurable timeout (default: 60s) after which unapproved actions automatically fail safe.

---

## 7. Audit Logging & Forensic Traceability

Every interaction, tool execution, safety evaluation, and user decision is permanently recorded in the local SQLite database (`app/database/agent.db`).

### 7.1 SQLite Schema: `action_audit_log`

```sql
CREATE TABLE IF NOT EXISTS action_audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT NOT NULL,
    step_number INTEGER NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    tier TEXT NOT NULL CHECK(tier IN ('READ_ONLY', 'CONTROLLED', 'APPROVAL_REQUIRED', 'RESTRICTED')),
    tool_name TEXT NOT NULL,
    action_type TEXT NOT NULL,
    target_app TEXT,
    target_window_title TEXT,
    target_element_selector TEXT,
    parameters_json TEXT,
    approval_status TEXT NOT NULL CHECK(approval_status IN ('AUTO_PERMITTED', 'APPROVED', 'REJECTED', 'BLOCKED', 'TIMEOUT')),
    execution_status TEXT NOT NULL CHECK(execution_status IN ('PENDING', 'SUCCESS', 'FAILED', 'ABORTED')),
    execution_time_ms REAL,
    error_message TEXT,
    before_state_hash TEXT,
    after_state_hash TEXT
);

CREATE INDEX IF NOT EXISTS idx_audit_task ON action_audit_log(task_id);
CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON action_audit_log(timestamp);
```

### 7.2 Privacy & Sensitive Data Scrubbing
Prior to writing parameters to `action_audit_log` or feeding state back to the LLM:
- Common password fields and credit card numbers are scrubbed using regular expression masks (`********`).
- Local filesystem user directories (`C:\Users\<username>`) can optionally be mapped to relative identifiers (`~`) in exportable logs.

---

## 8. Summary of Safety Invariants

| Safety Invariant | Rule | Enforcement Mechanism |
| :--- | :--- | :--- |
| **No Silent Destructive Actions** | Any file deletion, app closure, or form submission must have human sign-off. | Tier 3 `APPROVAL_REQUIRED` chat card. |
| **No Unbounded Loops** | Agent cannot loop infinitely on failing actions. | Hard cap of 25 steps per task; 3-stall circuit breaker. |
| **No Out-of-Focus Input** | Synthesized input cannot be sent to an unverified background window. | `WindowGuard` PID/HWND foreground check before every input. |
| **Immediate Operator Preemption** | User can instantly regain physical control of mouse/keyboard. | Global hotkey hook, mouse corner slam, UI cancel button. |
| **System File Immutability** | OS files and system registry keys can never be edited or deleted. | Tier 4 `RESTRICTED` hard rejection in `SafetyEnforcer`. |
| **100% Auditability** | Every single action attempt is preserved locally with forensic detail. | SQLite `action_audit_log` table with timing and status. |

---

## 9. Milestone C: Desktop Physical Actions & Coordinate Grounding Safety Model

Milestone C introduces controlled physical mouse and keyboard interaction. Because raw mouse clicks and keystrokes can affect any visible desktop element, strict physical safety boundaries are enforced:

### 9.1 Coordinate Grounding & Multi-Monitor Virtual Geometry
- **Normalized Scale [0, 1000]:** All agent-facing coordinates are specified on a canonical `[0, 1000]` scale, where `(0, 0)` is top-left and `(1000, 1000)` is bottom-right.
- **DPI Scaling & Virtual Screen Bounds:** Coordinates are mapped via Win32 virtual screen metrics (`SM_XVIRTUALSCREEN`, `SM_YVIRTUALSCREEN`, `SM_CXVIRTUALSCREEN`, `SM_CYVIRTUALSCREEN`), correctly supporting multi-monitor configurations and per-monitor DPI scaling.
- **Out-of-Bounds Rejection:** Any coordinate exceeding `[0, 1000]` or falling outside the physical desktop bounding box is rejected before input dispatch (`COORDINATES_OUT_OF_BOUNDS`).

### 9.2 Physical Input Safety Barriers (Tier 3 Approval)
- **Mandatory Confirmation Cards:** All mutating physical desktop actions (`move_mouse`, `click_at`, `double_click_at`, `right_click_at`, `drag_mouse`, `scroll_at`, `type_desktop_text`, `press_desktop_key`, `reset_emergency_stop`) require explicit user confirmation.
- **Read-Only Auto-Approval:** Display telemetry (`get_screen_metrics`) and the emergency stop circuit breaker (`trigger_emergency_stop`) are auto-approved for zero-latency execution.
- **No Auto-Enter Typing:** `type_desktop_text` simulates character typing with configurable delays (`delay_per_char`) without automatically appending newline/Enter.
- **Keyboard Allowlists:** Keystrokes are filtered against strict `SAFE_KEYS` and `SENSITIVE_KEYS` allowlists. Unauthorized keys are rejected with `KEY_NOT_ALLOWED`.

### 9.3 Global Emergency Stop Circuit Breaker
- **Failsafe Corner Slam:** Dragging the mouse to the extreme top-left corner `(0, 0)` or `<= 5px` immediately trips the circuit breaker.
- **Hardware Safety Release:** When tripped, synthetic `LEFTUP`, `RIGHTUP`, `MIDDLEUP`, `Ctrl`, `Alt`, `Shift`, and `Win` key releases are dispatched to prevent sticky input state.
- **Latching Halt:** Once activated, all subsequent physical input requests are immediately rejected with error code `EMERGENCY_STOP_ACTIVE`.
- **Deliberate Reset:** The circuit breaker cannot be cleared automatically; it requires an explicit `reset_emergency_stop` action with user confirmation.

