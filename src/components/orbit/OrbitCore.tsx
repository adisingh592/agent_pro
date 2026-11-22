import React from "react";
import { OrbitLogo } from "./OrbitLogo";

export const OrbitCore: React.FC = () => {
  return (
    <div className="relative z-20 flex flex-col items-center justify-center select-none">
      {/* Central energy glow sphere */}
      <div className="relative w-64 h-64 md:w-72 md:h-72 flex items-center justify-center">
        {/* Ambient radial aura behind the circle */}
        <div
          className="absolute inset-0 rounded-full blur-[45px] opacity-70 animate-orbit-pulse"
          style={{
            background: "radial-gradient(circle, rgba(155, 227, 74, 0.45) 0%, rgba(100, 184, 61, 0.2) 40%, transparent 70%)",
          }}
        />

        {/* Swirling Wavy Ribbon Aura (SVG fluid wave bands) */}
        <svg
          className="absolute inset-0 w-full h-full animate-swirl-cw pointer-events-none"
          viewBox="0 0 300 300"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <defs>
            <linearGradient id="wave-grad-1" x1="0" y1="0" x2="300" y2="300" gradientUnits="userSpaceOnUse">
              <stop offset="0%" stopColor="#C5FF67" stopOpacity="0.8" />
              <stop offset="40%" stopColor="#9BE34A" stopOpacity="0.4" />
              <stop offset="80%" stopColor="#66B83D" stopOpacity="0.1" />
              <stop offset="100%" stopColor="#C5FF67" stopOpacity="0.7" />
            </linearGradient>
            <linearGradient id="wave-grad-2" x1="300" y1="0" x2="0" y2="300" gradientUnits="userSpaceOnUse">
              <stop offset="0%" stopColor="#9BE34A" stopOpacity="0.7" />
              <stop offset="50%" stopColor="#C5FF67" stopOpacity="0.3" />
              <stop offset="100%" stopColor="#66B83D" stopOpacity="0.6" />
            </linearGradient>
          </defs>

          {/* Flowing multi-curve sine waves creating the silk ribbon aura from reference */}
          <path
            d="M 150 20 C 230 20, 280 80, 280 150 C 280 220, 220 280, 150 280 C 80 280, 20 220, 20 150 C 20 90, 70 20, 150 20 Z"
            stroke="url(#wave-grad-1)"
            strokeWidth="1.8"
            strokeDasharray="280 20"
            opacity="0.85"
          />
          <path
            d="M 150 35 C 220 15, 275 95, 265 160 C 255 225, 200 270, 135 265 C 70 260, 25 195, 35 130 C 45 65, 100 45, 150 35 Z"
            stroke="url(#wave-grad-2)"
            strokeWidth="1.4"
            opacity="0.6"
          />
          <path
            d="M 150 48 C 210 35, 255 105, 245 165 C 235 215, 185 255, 130 248 C 80 240, 48 185, 55 135 C 62 85, 110 55, 150 48 Z"
            stroke="url(#wave-grad-1)"
            strokeWidth="1"
            opacity="0.5"
          />
        </svg>

        {/* Counter-rotating subtle second wave ribbon */}
        <svg
          className="absolute inset-0 w-full h-full animate-swirl-ccw pointer-events-none opacity-50"
          viewBox="0 0 300 300"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M 150 30 Q 260 70 270 150 Q 250 240 150 270 Q 50 240 30 150 Q 50 50 150 30 Z"
            stroke="#9BE34A"
            strokeWidth="1"
            strokeDasharray="160 30"
          />
        </svg>

        {/* Inner Solid Translucent Core Circle */}
        <div className="relative w-52 h-52 rounded-full bg-[#07120A]/80 backdrop-blur-md border border-[rgba(155,227,74,0.35)] shadow-orbit-core flex flex-col items-center justify-center p-4 text-center">
          {/* Logo at center */}
          <div className="mb-2.5">
            <OrbitLogo size={42} glow={true} />
          </div>

          {/* Title: Personal Agent */}
          <h1 className="text-xl md:text-2xl font-bold tracking-tight text-[#F1F5ED] drop-shadow-[0_2px_8px_rgba(0,0,0,0.8)]">
            Personal Agent
          </h1>

          {/* Subtitle: Plan • Code • Automate • Execute */}
          <p className="mt-1 text-[11px] md:text-xs font-medium text-[#A4ADA2] tracking-wide">
            Plan <span className="text-[#9BE34A] opacity-80">•</span> Code <span className="text-[#9BE34A] opacity-80">•</span> Automate <span className="text-[#9BE34A] opacity-80">•</span> Execute
          </p>
        </div>
      </div>
    </div>
  );
};
