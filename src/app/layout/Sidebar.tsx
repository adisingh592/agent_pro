import React from "react";
import {
  MessageSquare,
  Monitor,
  LayoutGrid,
  Folder,
  CheckSquare,
  Brain,
  Activity,
  Settings,
  Plus,
  Bot,
  Circle
} from "lucide-react";
import { NavPage } from "../../types/agent";

interface SidebarProps {
  currentPage: NavPage;
  onNavigate: (page: NavPage) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ currentPage, onNavigate }) => {
  const navItems: { id: NavPage; label: string; icon: React.ReactNode }[] = [
    { id: "chat", label: "Chat", icon: <MessageSquare className="w-4 h-4" /> },
    { id: "computer", label: "Computer", icon: <Monitor className="w-4 h-4" /> },
    { id: "applications", label: "Applications", icon: <LayoutGrid className="w-4 h-4" /> },
    { id: "files", label: "Files", icon: <Folder className="w-4 h-4" /> },
    { id: "tasks", label: "Tasks", icon: <CheckSquare className="w-4 h-4" /> },
    { id: "memory", label: "Memory", icon: <Brain className="w-4 h-4" /> },
    { id: "activity", label: "Activity", icon: <Activity className="w-4 h-4" /> },
  ];

  return (
    <aside className="w-56 bg-bg-secondary border-r border-border-subtle flex flex-col justify-between shrink-0 select-none">
      {/* Top: Identity & New Chat */}
      <div className="p-3">
        {/* Brand identity */}
        <div className="flex items-center gap-2.5 px-2 py-1.5 mb-3">
          <div className="w-6 h-6 rounded bg-accent/15 border border-accent/30 flex items-center justify-center text-accent">
            <Bot className="w-3.5 h-3.5" />
          </div>
          <div>
            <div className="text-xs font-semibold tracking-wide text-text-primary">
              PERSONAL AGENT
            </div>
            <div className="text-[10px] text-text-muted">
              Autonomous Desktop AI
            </div>
          </div>
        </div>

        {/* New Chat Action */}
        <button
          onClick={() => onNavigate("chat")}
          className="w-full flex items-center justify-between px-3 py-1.5 rounded-md bg-bg-elevated hover:bg-bg-hover border border-border-subtle text-text-primary text-xs font-medium transition-colors group"
        >
          <span className="flex items-center gap-2">
            <Plus className="w-3.5 h-3.5 text-accent" />
            <span>New Chat</span>
          </span>
          <span className="text-[10px] text-text-muted group-hover:text-text-secondary">Ctrl+N</span>
        </button>

        {/* Main Navigation List */}
        <nav className="mt-4 space-y-0.5">
          {navItems.map((item) => {
            const isActive = currentPage === item.id;
            return (
              <button
                key={item.id}
                onClick={() => onNavigate(item.id)}
                className={`w-full flex items-center gap-2.5 px-2.5 py-1.5 rounded-md text-xs font-medium transition-all ${
                  isActive
                    ? "bg-accent/15 text-accent border border-accent/25"
                    : "text-text-secondary hover:text-text-primary hover:bg-bg-hover"
                }`}
              >
                <span className={isActive ? "text-accent" : "text-text-muted"}>
                  {item.icon}
                </span>
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>
      </div>

      {/* Bottom: Settings & System Status */}
      <div className="p-3 border-t border-border-subtle space-y-2">
        <button
          onClick={() => onNavigate("settings")}
          className={`w-full flex items-center gap-2.5 px-2.5 py-1.5 rounded-md text-xs font-medium transition-all ${
            currentPage === "settings"
              ? "bg-accent/15 text-accent border border-accent/25"
              : "text-text-secondary hover:text-text-primary hover:bg-bg-hover"
          }`}
        >
          <Settings className={`w-4 h-4 ${currentPage === "settings" ? "text-accent" : "text-text-muted"}`} />
          <span>Settings</span>
        </button>

        {/* Status card */}
        <div className="p-2 rounded bg-bg-elevated border border-border-subtle text-[11px] space-y-1">
          <div className="flex items-center justify-between">
            <span className="text-text-muted">Model</span>
            <span className="text-text-primary font-medium">qwen3:8b</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-text-muted">Backend</span>
            <span className="flex items-center gap-1.5 text-status-success font-medium">
              <Circle className="w-1.5 h-1.5 fill-status-success text-status-success" />
              Ollama Connected
            </span>
          </div>
        </div>
      </div>
    </aside>
  );
};
