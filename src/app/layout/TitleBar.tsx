import React from "react";
import { Search, Sparkles, Shield, Cpu } from "lucide-react";
import { NavPage } from "../../types/agent";

interface TitleBarProps {
  currentPage: NavPage;
  onNavigate: (page: NavPage) => void;
}

export const TitleBar: React.FC<TitleBarProps> = ({ currentPage, onNavigate }) => {
  return (
    <header className="h-10 border-b border-border-subtle bg-bg-main flex items-center justify-between px-4 select-none shrink-0">
      {/* Left: Window Title & Status */}
      <div className="flex items-center space-x-3 text-xs">
        <span className="font-semibold tracking-wider text-text-primary uppercase flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-accent animate-pulse" />
          Personal Agent
        </span>
        <span className="text-text-muted">|</span>
        <span className="text-text-secondary capitalize font-medium">
          {currentPage}
        </span>
      </div>

      {/* Center: Command / Search Bar */}
      <div className="flex-1 max-w-md mx-6">
        <div className="relative flex items-center">
          <Search className="w-3.5 h-3.5 text-text-muted absolute left-3 pointer-events-none" />
          <input
            type="text"
            readOnly
            onClick={() => onNavigate("chat")}
            placeholder="Search commands, tools, or files (Ctrl + K)"
            className="w-full h-7 bg-bg-secondary hover:bg-bg-elevated border border-border-subtle rounded-md pl-8 pr-12 text-xs text-text-secondary placeholder:text-text-muted cursor-pointer transition-colors"
          />
          <kbd className="absolute right-2 px-1.5 py-0.5 text-[10px] text-text-muted bg-bg-hover rounded border border-border-subtle">
            ⌘K
          </kbd>
        </div>
      </div>

      {/* Right: Telemetry & Safety Quick Indicators */}
      <div className="flex items-center space-x-3 text-xs">
        <div className="flex items-center gap-1.5 px-2 py-0.5 rounded bg-bg-secondary border border-border-subtle text-text-secondary text-[11px]">
          <Cpu className="w-3 h-3 text-accent" />
          <span>qwen3:8b (GPU)</span>
        </div>
        <div className="flex items-center gap-1.5 px-2 py-0.5 rounded bg-bg-secondary border border-border-subtle text-status-success text-[11px]">
          <Shield className="w-3 h-3" />
          <span>Safety Armed</span>
        </div>
      </div>
    </header>
  );
};
