import React from "react";
import { ChevronRight, LucideIcon } from "lucide-react";

interface NavigationPanelProps {
  id: string;
  title: string;
  subtitleLine1: string;
  subtitleLine2: string;
  icon: LucideIcon;
  onClick: () => void;
  className?: string;
}

export const NavigationPanel: React.FC<NavigationPanelProps> = ({
  id,
  title,
  subtitleLine1,
  subtitleLine2,
  icon: Icon,
  onClick,
  className = "",
}) => {
  return (
    <button
      onClick={onClick}
      className={`group relative flex items-center justify-between w-[270px] lg:w-[285px] h-[82px] px-5 py-3 rounded-[24px] text-left transition-all duration-300 ease-out select-none
        bg-[#09170F]/75 hover:bg-[#0E2417]/85 
        backdrop-blur-xl border border-[rgba(156,190,153,0.2)] hover:border-[#9BE34A]
        shadow-[0_4px_24px_rgba(0,0,0,0.45)] hover:shadow-[0_0_30px_rgba(155,227,74,0.3)]
        hover:scale-[1.02] hover:-translate-y-0.5 active:scale-[0.99] active:translate-y-0 cursor-pointer ${className}`}
    >
      {/* Soft inner corner light sweep */}
      <div className="absolute inset-0 rounded-[24px] opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none bg-gradient-to-r from-[rgba(155,227,74,0.1)] to-transparent" />

      {/* Left Icon + Text Block */}
      <div className="flex items-center gap-4 min-w-0 pr-2">
        {/* Glowing Lime Icon */}
        <div className="w-10 h-10 rounded-xl flex items-center justify-center shrink-0 text-[#9BE34A] group-hover:text-[#C5FF67] transition-colors">
          <Icon className="w-6 h-6 drop-shadow-[0_0_10px_rgba(155,227,74,0.65)] stroke-[2]" />
        </div>

        {/* Title and 2-line clean Subtitle matching reference */}
        <div className="min-w-0 flex-1">
          <div className="text-[15px] font-bold text-white tracking-tight group-hover:text-white transition-colors">
            {title}
          </div>
          <div className="text-[11.5px] text-[#95A594] group-hover:text-[#C2CEC1] leading-snug mt-0.5 transition-colors">
            <div>{subtitleLine1}</div>
            <div>{subtitleLine2}</div>
          </div>
        </div>
      </div>

      {/* Right subtle arrow chevron matching reference */}
      <div className="shrink-0 text-[#6F7D6E] group-hover:text-[#C5FF67] group-hover:translate-x-0.5 transition-all">
        <ChevronRight className="w-4 h-4 stroke-[2]" />
      </div>
    </button>
  );
};
