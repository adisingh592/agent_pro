import React from "react";
import { Search, Sparkles, Shield, Cpu, ArrowLeft } from "lucide-react";
import { NavPage } from "../../types/agent";
import { OrbitLogo } from "../../components/orbit/OrbitLogo";

interface TitleBarProps {
  currentPage: NavPage;
  onNavigate: (page: NavPage) => void;
}

export const TitleBar: React.FC<TitleBarProps> = ({ currentPage, onNavigate }) => {
  return (
    <header className="h-10 border-b border-[rgba(156,190,153,0.15)] bg-[#050907] flex items-center justify-between px-4 select-none shrink-0">
      {/* Left: Window Title & Status */}
      <div className="flex items-center space-x-3 text-xs">
        <button
          onClick={() => onNavigate("orbit")}
          className="flex items-center gap-1.5 px-2 py-0.5 rounded-md bg-[#0A160E] hover:bg-[#102417] border border-[rgba(155,227,74,0.3)] text-[#9BE34A] font-semibold tracking-wider text-[11px] transition-colors"
        >
          <ArrowLeft className="w-3 h-3" />
          <span>ORBIT</span>
        </button>
        <span className="text-[rgba(156,190,153,0.3)]">|</span>
        <span className="font-semibold tracking-wider text-[#F1F5ED] uppercase flex items-center gap-1.5 text-[11px]">
          Personal Agent
        </span>
        <span className="text-[rgba(156,190,153,0.3)]">/</span>
        <span className="text-[#9BE34A] capitalize font-medium text-[11px]">
          {currentPage}
        </span>
      </div>

      {/* Center: Command / Search Bar */}
      <div className="flex-1 max-w-md mx-6">
        <div className="relative flex items-center">
          <Search className="w-3.5 h-3.5 text-[#6F796F] absolute left-3 pointer-events-none" />
          <input
            type="text"
            readOnly
            onClick={() => onNavigate("chat")}
            placeholder="Search commands, tools, or files (Ctrl + K)"
            className="w-full h-7 bg-[#0A120C] hover:bg-[#0E1A11] border border-[rgba(156,190,153,0.18)] rounded-md pl-8 pr-12 text-xs text-[#A4ADA2] placeholder:text-[#6F796F] cursor-pointer transition-colors"
          />
          <kbd className="absolute right-2 px-1.5 py-0.5 text-[10px] text-[#6F796F] bg-[#0E1E13] rounded border border-[rgba(156,190,153,0.15)]">
            ⌘K
          </kbd>
        </div>
      </div>

      {/* Right: Telemetry & Safety Quick Indicators */}
      <div className="flex items-center space-x-3 text-xs">
        <div className="flex items-center gap-1.5 px-2 py-0.5 rounded bg-[#0A160E] border border-[rgba(156,190,153,0.15)] text-[#A4ADA2] text-[11px]">
          <Cpu className="w-3 h-3 text-[#9BE34A]" />
          <span>qwen3:8b (GPU)</span>
        </div>
        <div className="flex items-center gap-1.5 px-2 py-0.5 rounded bg-[#0A160E] border border-[rgba(156,190,153,0.15)] text-[#9BE34A] text-[11px]">
          <Shield className="w-3 h-3" />
          <span>Safety Armed</span>
        </div>
      </div>
    </header>
  );
};
