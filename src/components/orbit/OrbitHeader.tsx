import React, { useState } from "react";
import { OrbitLogo } from "./OrbitLogo";
import { Bell, Box, ChevronDown, Minus, Square, X } from "lucide-react";

interface OrbitHeaderProps {
  modelName?: string;
  onModelSelect?: (model: string) => void;
  onNavigateHome?: () => void;
}

export const OrbitHeader: React.FC<OrbitHeaderProps> = ({
  modelName = "Qwen3 8B",
  onModelSelect,
  onNavigateHome,
}) => {
  const [modelDropdownOpen, setModelDropdownOpen] = useState(false);
  const [hasNotification, setHasNotification] = useState(true);

  // Safe Tauri window management with fallback for browser testing
  const handleMinimize = async () => {
    try {
      const { getCurrentWindow } = await import("@tauri-apps/api/window");
      await getCurrentWindow().minimize();
    } catch {
      console.log("Window minimize (running in web browser preview)");
    }
  };

  const handleMaximize = async () => {
    try {
      const { getCurrentWindow } = await import("@tauri-apps/api/window");
      await getCurrentWindow().toggleMaximize();
    } catch {
      console.log("Window toggle maximize (running in web browser preview)");
    }
  };

  const handleClose = async () => {
    try {
      const { getCurrentWindow } = await import("@tauri-apps/api/window");
      await getCurrentWindow().close();
    } catch {
      console.log("Window close (running in web browser preview)");
    }
  };

  return (
    <header className="relative z-40 w-full h-14 md:h-16 px-5 flex items-center justify-between select-none">
      {/* Left: Branding & Tagline */}
      <div 
        onClick={onNavigateHome}
        className="flex items-center gap-3 cursor-pointer group"
      >
        <OrbitLogo size={32} glow={true} />
        <div className="flex flex-col">
          <span className="text-sm md:text-base font-bold tracking-tight text-[#F1F5ED] group-hover:text-white transition-colors">
            Personal Agent
          </span>
          <span className="text-[10px] md:text-[11px] text-[#A4ADA2] tracking-wide">
            Your AI Computer Companion
          </span>
        </div>
      </div>

      {/* Right: Status Pill, Model Selector, Notification Bell, Window Controls */}
      <div className="flex items-center gap-3">
        {/* Ollama Status Indicator Pill */}
        <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full bg-[#0A160E]/80 backdrop-blur-md border border-[rgba(156,190,153,0.18)] shadow-sm">
          <span className="w-2 h-2 rounded-full bg-[#9BE34A] shadow-[0_0_8px_#9BE34A] animate-pulse" />
          <span className="text-xs font-medium text-[#F1F5ED]">
            Ollama Connected
          </span>
        </div>

        {/* Model Selector Pill Dropdown */}
        <div className="relative">
          <button
            onClick={() => setModelDropdownOpen((prev) => !prev)}
            className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-[#0A160E]/80 hover:bg-[#102316]/90 backdrop-blur-md border border-[rgba(156,190,153,0.18)] hover:border-[rgba(155,227,74,0.4)] transition-all cursor-pointer text-xs font-medium text-[#F1F5ED]"
          >
            <Box className="w-3.5 h-3.5 text-[#9BE34A]" />
            <span>{modelName}</span>
            <ChevronDown className="w-3 h-3 text-[#A4ADA2]" />
          </button>

          {/* Model selection dropdown menu */}
          {modelDropdownOpen && (
            <div className="absolute right-0 mt-2 w-48 py-1.5 rounded-xl bg-[#08120B] border border-[rgba(155,227,74,0.3)] shadow-[0_10px_30px_rgba(0,0,0,0.8)] z-50">
              <div className="px-3 py-1 text-[10px] uppercase tracking-wider text-[#6F796F] font-semibold">
                Active Local Model
              </div>
              <button
                onClick={() => {
                  onModelSelect?.("Qwen3 8B");
                  setModelDropdownOpen(false);
                }}
                className="w-full text-left px-3 py-1.5 text-xs text-[#F1F5ED] hover:bg-[#112417] flex items-center justify-between"
              >
                <span>Qwen3 8B (Recommended)</span>
                <span className="w-1.5 h-1.5 rounded-full bg-[#9BE34A]" />
              </button>
              <button
                onClick={() => {
                  onModelSelect?.("Qwen2.5-Coder 7B");
                  setModelDropdownOpen(false);
                }}
                className="w-full text-left px-3 py-1.5 text-xs text-[#A4ADA2] hover:bg-[#112417] hover:text-[#F1F5ED]"
              >
                <span>Qwen2.5-Coder 7B</span>
              </button>
              <button
                onClick={() => {
                  onModelSelect?.("Llama 3.2 3B");
                  setModelDropdownOpen(false);
                }}
                className="w-full text-left px-3 py-1.5 text-xs text-[#A4ADA2] hover:bg-[#112417] hover:text-[#F1F5ED]"
              >
                <span>Llama 3.2 3B (Fast)</span>
              </button>
            </div>
          )}
        </div>

        {/* Notification Bell with Lime Green Dot */}
        <button
          onClick={() => setHasNotification(false)}
          title="Notifications & System Alerts"
          className="relative w-8 h-8 rounded-full flex items-center justify-center text-[#F1F5ED] hover:bg-[#102316]/90 border border-[rgba(156,190,153,0.18)] hover:border-[rgba(155,227,74,0.4)] transition-all cursor-pointer"
        >
          <Bell className="w-3.5 h-3.5 text-[#F1F5ED]" />
          {hasNotification && (
            <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 rounded-full bg-[#9BE34A] shadow-[0_0_6px_#9BE34A]" />
          )}
        </button>

        {/* Window Controls: Minimize, Maximize, Close */}
        <div className="flex items-center ml-2 border-l border-[rgba(156,190,153,0.15)] pl-2">
          <button
            onClick={handleMinimize}
            title="Minimize"
            className="w-8 h-8 flex items-center justify-center text-[#A4ADA2] hover:text-white hover:bg-[rgba(156,190,153,0.12)] rounded-md transition-colors"
          >
            <Minus className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={handleMaximize}
            title="Maximize"
            className="w-8 h-8 flex items-center justify-center text-[#A4ADA2] hover:text-white hover:bg-[rgba(156,190,153,0.12)] rounded-md transition-colors"
          >
            <Square className="w-3 h-3" />
          </button>
          <button
            onClick={handleClose}
            title="Close"
            className="w-8 h-8 flex items-center justify-center text-[#A4ADA2] hover:text-white hover:bg-red-500/80 rounded-md transition-colors"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </header>
  );
};
