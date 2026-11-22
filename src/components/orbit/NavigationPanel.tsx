import React from "react";
import { ChevronRight, LucideIcon } from "lucide-react";

interface NavigationPanelProps {
  id: string;
  title: string;
  subtitle: string;
  icon: LucideIcon;
  onClick: () => void;
  className?: string;
}

export const NavigationPanel: React.FC<NavigationPanelProps> = ({
  id,
  title,
  subtitle,
  icon: Icon,
  onClick,
  className = "",
}) => {
  return (
    <button
      onClick={onClick}
      className={`group relative flex items-center justify-between w-60 md:w-64 lg:w-72 h-[76px] px-4 py-3 rounded-2xl text-left transition-all duration-300 ease-out select-none
        bg-[#09150D]/75 hover:bg-[#0E2014]/90 
        backdrop-blur-xl border border-[rgba(156,190,153,0.18)] hover:border-[rgba(155,227,74,0.55)]
        shadow-[0_4px_20px_rgba(0,0,0,0.4)] hover:shadow-[0_0_30px_rgba(155,227,74,0.22)]
        hover:scale-[1.025] hover:-translate-y-0.5 active:scale-[0.99] active:translate-y-0 ${className}`}
    >
      {/* Subtle inner corner glow */}
      <div className="absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none bg-gradient-to-r from-[rgba(155,227,74,0.08)] to-transparent" />

      {/* Left Icon + Text details */}
      <div className="flex items-center gap-3.5 min-w-0 pr-2">
        {/* Icon in glowing lime accent */}
        <div className="w-10 h-10 rounded-xl flex items-center justify-center shrink-0 text-[#9BE34A] group-hover:text-[#C5FF67] transition-colors">
          <Icon className="w-5 h-5 drop-shadow-[0_0_8px_rgba(155,227,74,0.5)]" />
        </div>

        {/* Title and 2-line Subtitle */}
        <div className="min-w-0 flex-1">
          <div className="text-[14px] md:text-[15px] font-semibold text-[#F1F5ED] tracking-tight group-hover:text-white transition-colors">
            {title}
          </div>
          <div className="text-[11px] text-[#A4ADA2] group-hover:text-[#C3C9C1] leading-tight line-clamp-2 mt-0.5 transition-colors">
            {subtitle}
          </div>
        </div>
      </div>

      {/* Right subtle arrow chevron */}
      <div className="shrink-0 text-[#6F796F] group-hover:text-[#C5FF67] group-hover:translate-x-0.5 transition-all">
        <ChevronRight className="w-4 h-4" />
      </div>
    </button>
  );
};
