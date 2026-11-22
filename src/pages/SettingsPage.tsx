import React, { useState } from "react";
import {
  Settings,
  Cpu,
  Palette,
  Shield,
  Layers,
  Sliders,
  Check
} from "lucide-react";

type SettingsTab = "general" | "ai_models" | "appearance" | "automation" | "permissions" | "system";

export const SettingsPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<SettingsTab>("general");
  const [ollamaUrl, setOllamaUrl] = useState("http://localhost:11434");
  const [selectedModel, setSelectedModel] = useState("qwen3:8b");
  const [contextWindow, setContextWindow] = useState("4096");
  const [autoApproval, setAutoApproval] = useState(false);
  const [cornerSlamFailsafe, setCornerSlamFailsafe] = useState(true);

  const tabs: { id: SettingsTab; label: string; icon: React.ReactNode }[] = [
    { id: "general", label: "General", icon: <Sliders className="w-3.5 h-3.5" /> },
    { id: "ai_models", label: "AI & Models", icon: <Cpu className="w-3.5 h-3.5" /> },
    { id: "appearance", label: "Appearance", icon: <Palette className="w-3.5 h-3.5" /> },
    { id: "automation", label: "Automation", icon: <Layers className="w-3.5 h-3.5" /> },
    { id: "permissions", label: "Permissions & Safety", icon: <Shield className="w-3.5 h-3.5" /> },
    { id: "system", label: "System Telemetry", icon: <Settings className="w-3.5 h-3.5" /> },
  ];

  return (
    <div className="flex-1 flex flex-col h-full overflow-hidden p-6 space-y-4">
      {/* Header */}
      <div className="pb-3 border-b border-border-subtle shrink-0">
        <h1 className="text-lg font-semibold text-text-primary tracking-tight flex items-center gap-2">
          <Settings className="w-5 h-5 text-accent" />
          Application Settings
        </h1>
        <p className="text-xs text-text-muted mt-0.5">
          Configure model parameters, local hardware acceleration, safety boundaries, and UI behavior.
        </p>
      </div>

      {/* Settings Navigation & Content Panel */}
      <div className="flex-1 flex gap-6 overflow-hidden">
        {/* Left Settings Sidebar */}
        <div className="w-48 shrink-0 space-y-1">
          {tabs.map((tab) => {
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`w-full flex items-center gap-2.5 px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
                  isActive
                    ? "bg-accent/15 text-accent border border-accent/25"
                    : "text-text-secondary hover:text-text-primary hover:bg-bg-hover"
                }`}
              >
                <span>{tab.icon}</span>
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>

        {/* Right Settings Content Area */}
        <div className="flex-1 bg-bg-secondary border border-border-subtle rounded-lg p-5 overflow-y-auto space-y-5 text-xs">
          {activeTab === "general" && (
            <div className="space-y-4">
              <h2 className="text-sm font-semibold text-text-primary">General Configuration</h2>
              <div className="space-y-1.5">
                <label className="text-text-secondary block">Application Name</label>
                <input
                  type="text"
                  value="Personal Agent"
                  disabled
                  className="w-full max-w-sm h-8 bg-bg-main border border-border-subtle rounded px-2.5 text-text-primary opacity-80"
                />
              </div>
              <div className="space-y-1.5">
                <label className="text-text-secondary block">Workspace Root</label>
                <input
                  type="text"
                  value="h:\pro agent"
                  disabled
                  className="w-full max-w-sm h-8 bg-bg-main border border-border-subtle rounded px-2.5 font-mono text-text-primary opacity-80"
                />
              </div>
            </div>
          )}

          {activeTab === "ai_models" && (
            <div className="space-y-4">
              <h2 className="text-sm font-semibold text-text-primary">Local LLM & Hardware Acceleration</h2>
              <div className="space-y-1.5">
                <label className="text-text-secondary block">Ollama Daemon API Endpoint</label>
                <input
                  type="text"
                  value={ollamaUrl}
                  onChange={(e) => setOllamaUrl(e.target.value)}
                  className="w-full max-w-sm h-8 bg-bg-main border border-border-subtle rounded px-2.5 font-mono text-text-primary focus:border-accent/60 outline-none"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-text-secondary block">Active Model</label>
                <select
                  value={selectedModel}
                  onChange={(e) => setSelectedModel(e.target.value)}
                  className="w-full max-w-sm h-8 bg-bg-main border border-border-subtle rounded px-2.5 text-text-primary outline-none"
                >
                  <option value="qwen3:8b">qwen3:8b (5.2 GB GGUF, CUDA Accelerated)</option>
                  <option value="llama3.1:8b">llama3.1:8b</option>
                  <option value="mistral:7b">mistral:7b</option>
                </select>
              </div>

              <div className="space-y-1.5">
                <label className="text-text-secondary block">Context Window Size (Tokens)</label>
                <input
                  type="text"
                  value={contextWindow}
                  onChange={(e) => setContextWindow(e.target.value)}
                  className="w-full max-w-sm h-8 bg-bg-main border border-border-subtle rounded px-2.5 font-mono text-text-primary focus:border-accent/60 outline-none"
                />
                <span className="text-[10px] text-text-muted block">
                  Bounded to 4096 tokens to ensure GPU memory allocation does not exceed 6GB VRAM on RTX 3050.
                </span>
              </div>
            </div>
          )}

          {activeTab === "appearance" && (
            <div className="space-y-4">
              <h2 className="text-sm font-semibold text-text-primary">Theme & Appearance</h2>
              <p className="text-text-secondary">
                Personal Agent uses a custom dark theme inspired by Linear and Claude Desktop with warm amber accents.
              </p>
              <div className="flex items-center gap-3">
                <div className="w-16 h-12 rounded bg-bg-main border-2 border-accent flex items-center justify-center text-[10px] font-semibold text-accent">
                  Dark
                </div>
                <div className="w-16 h-12 rounded bg-bg-secondary border border-border-subtle flex items-center justify-center text-[10px] text-text-muted opacity-50 cursor-not-allowed">
                  Light
                </div>
              </div>
            </div>
          )}

          {activeTab === "automation" && (
            <div className="space-y-4">
              <h2 className="text-sm font-semibold text-text-primary">Computer Control & Grounding</h2>
              <div className="space-y-3">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={cornerSlamFailsafe}
                    onChange={(e) => setCornerSlamFailsafe(e.target.checked)}
                    className="accent-accent"
                  />
                  <span>Enable Corner Slam Failsafe (Moving mouse to (0,0) aborts automation)</span>
                </label>
                <div className="text-[10px] text-text-muted pl-5">
                  PyAutoGUI-style safety standard: Any physical mouse movement to the screen corners trips the emergency stop immediately.
                </div>
              </div>
            </div>
          )}

          {activeTab === "permissions" && (
            <div className="space-y-4">
              <h2 className="text-sm font-semibold text-text-primary">4-Tier Safety Policy & Approval</h2>
              <div className="space-y-3">
                <div className="p-3 rounded bg-bg-main border border-border-subtle space-y-1">
                  <div className="font-semibold text-accent">Human-in-the-Loop Mode (Enforced)</div>
                  <p className="text-[11px] text-text-muted">
                    All mutating desktop operations (application launch, process close, file modification, mouse clicks, and typing) stage an interactive confirmation card in the chat UI.
                  </p>
                </div>
              </div>
            </div>
          )}

          {activeTab === "system" && (
            <div className="space-y-3 font-mono text-[11px]">
              <h2 className="text-sm font-semibold text-text-primary font-sans">System Diagnostics</h2>
              <div className="bg-bg-main p-3 rounded border border-border-subtle space-y-1 text-text-secondary">
                <div>OS: Windows 11 (x64)</div>
                <div>CPU: 13th Gen Intel Core i7-13650HX</div>
                <div>GPU: NVIDIA GeForce RTX 3050 Laptop GPU (6GB VRAM)</div>
                <div>Frontend: Tauri 2 + React 18 + TypeScript + Vite + Tailwind CSS</div>
                <div>Backend Engine: Python 3.12+ / PySide6 / Ollama qwen3:8b</div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
