# PERSONAL AGENT — AUTONOMOUS TASK EXECUTION & REPAIR ENGINE
**Document Version:** 1.0.0  
**Phase:** Computer Automation Engine (Milestone A)  
**Target Architecture:** ReAct Desktop Loop / Hierarchical Task Planner / Deterministic Verification / Skill Replay

---

## 1. Overview & Purpose

Autonomous desktop task execution requires an AI agent to translate open-ended natural language requests (e.g., *"Open VS Code, create a new file called `benchmark.py`, paste the performance script, and run it in the integrated terminal"*) into a sequence of atomic, safe, and verifiable operating system actions.

A naive single-pass execution model (*"generate plan → run all steps"*) fails in real-world desktop environments due to:
- Dynamic UI latency (applications take variable milliseconds to open or render).
- Pop-ups, modal dialogs, and unexpected window focus shifts.
- Dynamic control IDs and fluctuating layout coordinates.
- Silent failures (e.g., clicking a button that was disabled or obstructed).

To achieve industrial-grade reliability on Windows 11, Personal Agent implements an **Observe → Ground → Act → Verify (OGAV) ReAct Engine** combined with **deterministic state assertions**, **closed-loop error recovery**, and **reusable persistent skill memory**.

---

## 2. The Core Desktop ReAct Loop (OGAV Architecture)

```
                    +------------------------------------+
                    |       USER TASK INSTRUCTION        |
                    +-----------------+------------------+
                                      |
                                      v
                    +------------------------------------+
                    |        TASK PLANNER & GOAL         |
                    |    (Decompose into Sub-Goals)      |
                    +-----------------+------------------+
                                      |
             +------------------------+<-------------------------+
             |                                                   |
             v                                                   | (Next Step
+----------------------------+                                   |  or Re-plan)
| 1. OBSERVE DESKTOP STATE   |                                   |
| - Active HWND / Process    |                                   |
| - UI Automation Tree       |                                   |
| - Screen Hash / Telemetry  |                                   |
+-------------+--------------+                                   |
              |                                                  |
              v                                                  |
+----------------------------+                                   |
| 2. GROUND ACTION           |                                   |
| - Priority 1: Direct API   |                                   |
| - Priority 2: UI Auto Tree |                                   |
| - Priority 3: Browser DOM  |                                   |
| - Priority 4: Visual/Coord |                                   |
| - Resolve target & bounds  |                                   |
+-------------+--------------+                                   |
              |                                                  |
              v                                                  |
+----------------------------+                                   |
| 3. SAFETY CHECK & ACT      |                                   |
| - Tier 1/2: Auto-execute   |                                   |
| - Tier 3: User Staged Card |                                   |
| - Dispatch atomic input    |                                   |
+-------------+--------------+                                   |
              |                                                  |
              v                                                  |
+----------------------------+                                   |
| 4. VERIFY STATE CHANGE     |                                   |
| - Did target window open?  |                                   |
| - Did UI element mutate?   |                                   |
| - Did file appear on disk? |                                   |
+-------------+--------------+                                   |
              |                                                  |
     +--------+--------+                                         |
     | Verification    |                                         |
     v                 v                                         |
[ SUCCESS ]       [ FAILURE ]                                    |
     |                 |                                         |
     | Advance         v                                         |
     | Step     +----------------------------+                   |
     |          | RECOVERY & RE-PLAN         |                   |
     |          | - Fallback interaction tier|                   |
     |          | - Dismiss blocking dialog  |                   |
     |          | - Refresh UI tree & retry  |                   |
     |          +--------------+-------------+                   |
     |                         |                                 |
     +-------------------------+---------------------------------+
                               |
                        (All Goals Done)
                               v
                    +------------------------------------+
                    |      TASK COMPLETED REPORT         |
                    |   (Emit final response to user)    |
                    +------------------------------------+
```

---

## 3. Dynamic Task Planner & State Machine

Complex tasks are handled via a hierarchical state machine managed by `TaskPlanner`.

### 3.1 Task Decomposition Schema
When a user submits a multi-step instruction, `TaskPlanner` invokes `qwen3:8b` with a specialized structured decomposition prompt to produce a `TaskPlan`:

```python
class TaskPlan(BaseModel):
    task_id: str                      # Unique UUIDv4 identifier
    title: str                        # Human-readable title
    user_prompt: str                  # Original user instruction
    sub_goals: list[SubGoal]          # Ordered sequence of major milestones
    current_sub_goal_idx: int = 0
    total_steps_executed: int = 0
    max_steps_allowed: int = 25       # Invariant safety bound
    status: TaskStatus = TaskStatus.PENDING

class SubGoal(BaseModel):
    goal_id: str
    description: str
    target_app: str                   # e.g., "Visual Studio Code"
    expected_outcome: str             # e.g., "Editor window visible with benchmark.py open"
    steps: list[ActionCommand]
    status: GoalStatus = GoalStatus.PENDING
```

### 3.2 Action State Machine
Each atomic action progresses through explicit states:

```
[ PENDING ] ──> [ STAGED_APPROVAL ] ──> [ EXECUTING ] ──> [ VERIFYING ] ──> [ COMPLETED ]
                      │                                         │
                      └──> [ REJECTED ]                         └──> [ FAILED ]
                                                                        │
                                                                        v
                                                                 [ RE-PLANNING ]
```

---

## 4. Deterministic Verification Rules

Actions must **never** be assumed successful simply because a click or keystroke was dispatched. The agent evaluates deterministic state assertions following every action.

| Action Type | Verification Rule | Assertion Method | Timeout |
| :--- | :--- | :--- | :--- |
| **Launch App** | Target process PID is running and main window handle (`HWND`) is visible. | `psutil.process_iter()`, Win32 `IsWindowVisible(hwnd)`. | 5000 ms |
| **Focus Window** | Foreground window matches target HWND. | Win32 `GetForegroundWindow() == target_hwnd`. | 1500 ms |
| **Click Button** | Button state transitions (e.g. `ToggleState` changes, dialog closes, or new window opens). | UI Automation `TogglePattern`, window count diff, or visual diff hash. | 2000 ms |
| **Type Text** | Text property of target input control contains the expected substring. | UI Automation `ValuePattern.Value` or `TextPattern.GetText()`. | 1500 ms |
| **Close App** | Process PID is terminated and removed from operating system process table. | `psutil.pid_exists(pid) == False`. | 3000 ms |
| **File Operation** | File exists on disk and byte size matches target. | `os.path.exists(path)` and `os.path.getsize(path) > 0`. | 1000 ms |
| **Browser Navigate** | Document readyState is `complete` and page URL matches expected pattern. | Playwright/CDP `page.url()` and `domcontentloaded`. | 8000 ms |

If an assertion fails within the timeout, the action is marked `VERIFICATION_FAILED` and routed to the **Error Recovery Engine**.

---

## 5. Error Recovery & Replanning Engine

When an atomic action or verification fails, the agent does not immediately abort the task. It employs a multi-tier recovery protocol:

```
+---------------------------------------------------------------------------------+
|                           ERROR RECOVERY PROTOCOL                               |
+---------------------------------------------------------------------------------+
| Level 1: Transient Latency Retry                                                |
|   - Re-check verification assertion after a 500ms delay.                        |
|   - Handles slow UI renders and asynchronous window paints.                     |
|                                                                                 |
| Level 2: Target Grounding Refresh                                               |
|   - Invalidate cached UI Automation tree.                                       |
|   - Re-query accessibility nodes from desktop root.                             |
|   - Search for matching control by alternative attributes (Name, AutomationId,  |
|     LocalizedControlType, ClassName).                                           |
|                                                                                 |
| Level 3: Modal Dialog / Pop-up Dismissal                                        |
|   - Detect if an unexpected child modal or warning dialog has appeared.         |
|   - Read modal dialog title and text.                                           |
|   - If it is a non-destructive prompt (e.g., "Tip of the Day", "Update Available",|
|     or "Restore Session"), dismiss it safely or report to user.                 |
|                                                                                 |
| Level 4: Fallback to Next Interaction Priority                                  |
|   - Level 2 (UI Automation) failed -> Fallback to Level 4 (Visual coordinate    |
|     grounding via UI screenshot).                                               |
|   - Level 4 failed -> Fallback to Level 5 (OCR text box centroid click).       |
|                                                                                 |
| Level 5: Goal Re-planning with LLM                                              |
|   - Feed error context, screenshot summary, and failed action back to Qwen.     |
|   - Request alternative action sequence to achieve the same sub-goal.           |
|                                                                                 |
| Terminal Escalation: Ask User                                                   |
|   - If 3 consecutive replanning attempts fail, pause execution, alert user in  |
|     chat with exact diagnostic report, and request human guidance.              |
+---------------------------------------------------------------------------------+
```

---

## 6. Execution Invariants & Loop Bounds

To ensure the agent remains fully deterministic, stable, and resource-bounded, the following invariants are strictly enforced by the execution engine:

1. **Step Bound Invariant:** Maximum **25 atomic steps** per task. If a task exceeds 25 steps, the agent forces a pause and requires user authorization to continue.
2. **Action Timeout Invariant:** Every atomic action has a hard timeout of **10 seconds**. An action that blocks for > 10s is killed and treated as a failure.
3. **Total Task Timeout Invariant:** The entire task has an overall wall-clock timeout of **300 seconds (5 minutes)**.
4. **Stall Detection (Loop Guard):** The agent computes a perceptual hash (`pHash`) and accessibility tree node count before and after each action. If **3 consecutive actions** result in identical state hashes without advancing the sub-goal, the agent triggers an automatic stall alert and halts.
5. **No Blind Keystrokes:** The agent must never type characters without first verifying that a valid text-entry control has keyboard focus.

---

## 7. Persistent Skill Memory & Trajectory Replay

When the agent successfully completes a multi-step task, the execution sequence can be saved into the **Skill Memory Store** for instant, zero-LLM replay in the future.

### 7.1 SQLite Schema: `skills` and `skill_steps`

```sql
CREATE TABLE IF NOT EXISTS skills (
    skill_id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL,
    category TEXT DEFAULT 'desktop_automation',
    parameters_schema JSON,           -- JSON Schema defining dynamic inputs (e.g., file path, text)
    preconditions JSON,               -- Required running apps, OS version, minimum screen res
    postconditions JSON,              -- Verification assertions to confirm successful replay
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_executed DATETIME,
    success_count INTEGER DEFAULT 0,
    failure_count INTEGER DEFAULT 0,
    avg_duration_ms REAL
);

CREATE TABLE IF NOT EXISTS skill_steps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    skill_id TEXT NOT NULL,
    step_number INTEGER NOT NULL,
    tool_name TEXT NOT NULL,
    action_type TEXT NOT NULL,
    target_selector JSON NOT NULL,     -- UI Automation selector, App name, or coordinate ratio
    parameters_template JSON NOT NULL, -- May contain parameterized variables e.g. {{file_name}}
    expected_state JSON,
    FOREIGN KEY(skill_id) REFERENCES skills(skill_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_skill_name ON skills(name);
CREATE INDEX IF NOT EXISTS idx_skill_steps ON skill_steps(skill_id, step_number);
```

### 7.2 Skill Replay Execution Mechanics
1. **Parameterized Substitution:** When executing a stored skill (e.g. `save_document(name="report.docx")`), variables in `parameters_template` are substituted with runtime arguments.
2. **Precondition Check:** Verifies that required applications are open and ready before executing step 1.
3. **Deterministic Step-by-Step Execution:** Dispatches each step sequentially, verifying expected state changes after every step.
4. **Fast-Path Acceleration:** Bypasses LLM token generation completely, executing the workflow in sub-seconds.
5. **Drift Detection:** If a UI control has changed location or title, the replay aborts gracefully and drops back into the full ReAct LLM loop to repair the step.
