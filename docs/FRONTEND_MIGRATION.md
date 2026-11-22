# PERSONAL AGENT — FRONTEND MIGRATION DOCUMENTATION
**Milestone:** Milestone 1 — Modern Desktop UI Foundation  
**Target Environment:** Windows 11 Desktop (Tauri 2 + React + TypeScript + Vite + Tailwind CSS)  
**Backend:** Existing Python Agent Core (`app/`, Ollama `qwen3:8b`, SQLite, Tool Registry, Windows UI Automation, Desktop Actions) — **Preserved Intact**

---

## 1. Executive Migration Overview

Personal Agent is evolving its desktop presentation layer from PySide6 to a modern desktop application powered by **Tauri 2**, **React 18**, **TypeScript**, **Vite**, and **Tailwind CSS**.

### Strict Architectural Boundaries
- **Python Backend Intact:** The existing Python agent (`app/`), Ollama client, 44 registered tools, 4-tier safety engine, Windows UI Automation, and physical desktop action grounding remain 100% untouched and functional.
- **No Secondary Agent Engine:** The frontend does not replicate or re-implement LLM reasoning or automation logic. It serves purely as a desktop command center and visualization surface.
- **Clean Service Abstraction:** `src/services/api.ts` defines typed interfaces preparing for IPC/HTTP communication with the local Python backend in Milestone 2.

---

## 2. Frontend Technology Stack

| Layer | Selected Technology | Configuration & Purpose |
| :--- | :--- | :--- |
| **Desktop Shell** | **Tauri 2.0+** | Rust-based lightweight desktop wrapper using Microsoft Edge WebView2 |
| **Frontend Framework** | **React 18** | Functional components with TypeScript hooks |
| **Language** | **TypeScript 5.6** | Full type safety (`@/types/agent.ts`) with zero `any` |
| **Build & Dev Tool** | **Vite 5.4** | Fast HMR dev server on port `1420` and optimized production builds |
| **Styling** | **Tailwind CSS 3.4** | Custom dark theme inspired by Claude Desktop, Linear, and Raycast |
| **Icons** | **Lucide React** | Consistent, refined iconography across sidebar, badges, and controls |
| **Animations** | **Framer Motion** | Subtle, high-performance transitions for pages and cards |

---

## 3. Design System & Palette

| Token | Hex Value | Usage |
| :--- | :--- | :--- |
| **Main Background** | `#111210` | Primary application viewport and root shell |
| **Secondary Background** | `#181917` | Navigation sidebar, title bar, and message cards |
| **Elevated Background** | `#1E201E` | User message bubbles, telemetry stat cards, buttons |
| **Hover Background** | `#252824` | Interactive hover states |
| **Borders** | `#2B2D2A` | Refined separation lines and container boundaries |
| **Primary Text** | `#EAECE7` | Main headings, user prompts, assistant text |
| **Secondary Text** | `#999E96` | Subheadings, descriptions, metadata |
| **Muted Text** | `#686D66` | Keyboard hints, timestamps, disabled labels |
| **Primary Accent** | `#D9A45B` | Active navigation highlights, primary send button, badges |
| **Accent Hover** | `#E7B66F` | Focused interactions and active hover |
| **Status Green** | `#5A9E66` | Online state, completed tools, healthy gauges |
| **Status Amber** | `#D48B38` | Staged confirmation cards, warnings |
| **Status Red** | `#C45A55` | Emergency stop, critical errors |

---

## 4. Frontend Component & Page Architecture

```
src/
├── app/
│   ├── App.tsx                  # Root state & page switcher
│   └── layout/
│       ├── AppLayout.tsx        # Persistent shell (TitleBar + Sidebar + Page Viewport)
│       ├── Sidebar.tsx          # Compact navigation rail, identity & model status
│       └── TitleBar.tsx         # Command bar (Ctrl+K), title & status telemetry
├── components/
│   └── chat/
│       ├── EmptyChatState.tsx   # Premium empty state with 4 suggestion cards
│       └── ToolActivityBadge.tsx# Embedded tool execution and confirmation cards
├── pages/
│   ├── ChatPage.tsx             # Primary conversational interface with composer
│   ├── ComputerPage.tsx         # Live desktop telemetry, active window & failsafe status
│   ├── ApplicationsPage.tsx     # Installed apps list, search, category filters & launch
│   ├── FilesPage.tsx            # Workspace explorer, breadcrumbs & file table
│   ├── TasksPage.tsx            # Task priority queues and scheduled workflows
│   ├── MemoryPage.tsx           # Searchable long-term agent memory and facts
│   ├── ActivityPage.tsx         # Forensic audit timeline with duration badges
│   └── SettingsPage.tsx         # 6-section settings navigator (AI, Automation, Safety)
├── lib/
│   ├── mockData.ts              # Cleanly isolated mock datasets (IS_MOCK_DATA = true)
│   └── utils.ts                 # cn() class merging helper
├── services/
│   └── api.ts                   # Typed API client preparing for Python backend bridge
├── types/
│   └── agent.ts                 # TypeScript domain contracts
├── index.css                    # Tailwind directives, custom scrollbars, dark base
└── main.tsx                     # React application entry point
```

---

## 5. Development & Build Commands

### Prerequisites
- **Node.js**: v20+ (v24.14.0 verified)
- **Rust & Cargo**: v1.80+ (v1.100.0 verified)
- **WebView2**: Evergreen runtime (installed on Windows 11)

### Commands
```bash
# 1. Install frontend dependencies
npm install

# 2. Run Vite frontend dev server (standalone in browser)
npm run dev
# URL: http://localhost:1420

# 3. Build optimized production bundle
npm run build
# Compiles to dist/ (HTML, CSS, JS)

# 4. Run Tauri desktop application
npm run tauri -- dev
```

---

## 6. Mock Data & Isolation Policy

In this milestone, backend integration is intentionally deferred to prevent disrupting the active Python engine:
- All placeholder data is centralized in `src/lib/mockData.ts`.
- The flag `export const IS_MOCK_DATA = true;` marks all placeholder state.
- No simulated action claims to have physically manipulated files or processes without confirmation.
- In Milestone 2, `src/services/api.ts` will connect directly to the local Python agent via HTTP/WebSocket or local IPC.
