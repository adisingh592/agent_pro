import React from "react";
import {
  Sparkles,
  MessageSquare,
  Monitor,
  Code2,
  Zap,
  LayoutGrid,
  Clock,
  Folder,
  CheckSquare,
  Brain,
  Settings,
  Plus,
} from "lucide-react";
import { NavPage } from "../../types/agent";
import { OrbitLogo } from "../../components/orbit/OrbitLogo";

interface SidebarProps {
  currentPage: NavPage;
  onNavigate: (page: NavPage) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ currentPage, onNavigate }) => {
  const mainNavItems: { id: NavPage; label: string; icon: React.ReactNode }[] = [
    { id: "orbit", label: "Orbit Home", icon: <OrbitLogo size={18} glow={false} /> },
    { id: "rooms", label: "Nine Rooms Deck", icon: <Sparkles className="w-4 h-4 text-[#8BE9FF]" /> },
    { id: "chat", label: "Chat Assistant", icon: <MessageSquare className="w-4 h-4" /> },
    { id: "ide", label: "IDE Workspace", icon: <Code2 className="w-4 h-4" /> },
    { id: "automation", label: "Automation", icon: <Zap className="w-4 h-4" /> },
    { id: "computer", label: "Agent & Screen", icon: <Monitor className="w-4 h-4" /> },
    { id: "skills", label: "Skills & Tools", icon: <LayoutGrid className="w-4 h-4" /> },
    { id: "activity", label: "Execution History", icon: <Clock className="w-4 h-4" /> },
    { id: "files", label: "Safe Files", icon: <Folder className="w-4 h-4" /> },
    { id: "tasks", label: "Task Queue", icon: <CheckSquare className="w-4 h-4" /> },
    { id: "memory", label: "Agent Memory", icon: <Brain className="w-4 h-4" /> },
  ];

  return (
    <aside className="w-56 bg-[#071009] border-r border-[rgba(156,190,153,0.15)] flex flex-col justify-between shrink-0 select-none">
      {/* Top: Identity & Navigation */}
      <div className="p-3">
        {/* Brand identity */}
        <div 
          onClick={() => onNavigate("orbit")}
          className="flex items-center gap-2.5 px-2 py-1.5 mb-3 cursor-pointer group"
        >
          <OrbitLogo size={26} glow={true} />
          <div>
            <div className="text-xs font-bold tracking-wide text-[#F1F5ED] group-hover:text-white transition-colors">
              PERSONAL AGENT
            </div>
            <div className="text-[10px] text-[#A4ADA2]">
              Orbit Environment
            </div>
          </div>
        </div>

        {/* Orbit Home Return Action */}
        <button
          onClick={() => onNavigate("orbit")}
          className="w-full mb-2 flex items-center justify-between px-3 py-1.5 rounded-lg bg-[#0E2214] hover:bg-[#163520] border border-[rgba(155,227,74,0.35)] text-[#9BE34A] text-xs font-semibold transition-all group shadow-[0_0_12px_rgba(155,227,74,0.15)]"
        >
          <span className="flex items-center gap-2">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Return to Orbit</span>
          </span>
          <span className="text-[10px] text-[#A4ADA2] group-hover:text-white">Esc</span>
        </button>

        {/* New Chat Action */}
        <button
          onClick={() => onNavigate("chat")}
          className="w-full flex items-center justify-between px-3 py-1.5 rounded-lg bg-[#0A160E] hover:bg-[#112417] border border-[rgba(156,190,153,0.15)] text-[#F1F5ED] text-xs font-medium transition-colors group mb-3"
        >
          <span className="flex items-center gap-2">
            <Plus className="w-3.5 h-3.5 text-[#9BE34A]" />
            <span>New Chat</span>
          </span>
          <span className="text-[10px] text-[#6F796F]">Ctrl+N</span>
        </button>

        {/* Navigation List */}
        <nav className="space-y-0.5">
          {mainNavItems.map((item) => {
            const isActive = currentPage === item.id;
            return (
              <button
                key={item.id}
                onClick={() => onNavigate(item.id)}
                className={`w-full flex items-center gap-2.5 px-2.5 py-1.5 rounded-lg text-xs font-medium transition-all ${
                  isActive
                    ? "bg-[#0E2014] text-[#9BE34A] border border-[rgba(155,227,74,0.35)] shadow-[0_0_10px_rgba(155,227,74,0.12)]"
                    : "text-[#A4ADA2] hover:text-[#F1F5ED] hover:bg-[#0E1E12]"
                }`}
              >
                <span className={isActive ? "text-[#9BE34A]" : "text-[#6F796F]"}>
                  {item.icon}
                </span>
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>
      </div>

      {/* Bottom: Settings & System Status */}
      <div className="p-3 border-t border-[rgba(156,190,153,0.15)] space-y-2">
        <button
          onClick={() => onNavigate("settings")}
          className={`w-full flex items-center gap-2.5 px-2.5 py-1.5 rounded-lg text-xs font-medium transition-all ${
            currentPage === "settings"
              ? "bg-[#0E2014] text-[#9BE34A] border border-[rgba(155,227,74,0.35)]"
              : "text-[#A4ADA2] hover:text-[#F1F5ED] hover:bg-[#0E1E12]"
          }`}
        >
          <Settings className={`w-4 h-4 ${currentPage === "settings" ? "text-[#9BE34A]" : "text-[#6F796F]"}`} />
          <span>Settings</span>
        </button>

        <div className="px-2 py-1.5 rounded-md bg-[#050C07] border border-[rgba(156,190,153,0.1)] text-[11px] text-[#6F796F] flex items-center justify-between">
          <span className="flex items-center gap-1.5 text-[#9BE34A]">
            <span className="w-1.5 h-1.5 rounded-full bg-[#9BE34A] animate-pulse" />
            Ollama Ready
          </span>
          <span>qwen3:8b</span>
        </div>
      </div>
    </aside>
  );
};
