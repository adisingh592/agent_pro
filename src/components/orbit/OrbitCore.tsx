import React from "react";
import { OrbitLogo } from "./OrbitLogo";

export const OrbitCore: React.FC = () => {
  return (
    <div className="relative z-20 flex flex-col items-center justify-center select-none">
      {/* Central energy glow sphere */}
      <div className="relative w-72 h-72 lg:w-80 lg:h-80 flex items-center justify-center">
        {/* Soft background ambient radial aura */}
        <div
          className="absolute inset-0 rounded-full blur-[50px] opacity-75 animate-orbit-pulse"
          style={{
            background: "radial-gradient(circle, rgba(155, 227, 74, 0.45) 0%, rgba(80, 170, 50, 0.2) 45%, transparent 70%)",
          }}
        />

        {/* Dynamic 3D Silk Wave Ribbons swirling around the core (Clockwise) */}
        <svg
          className="absolute inset-0 w-full h-full animate-swirl-cw pointer-events-none"
          viewBox="0 0 320 320"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <defs>
            <linearGradient id="silk-grad-1" x1="20" y1="20" x2="300" y2="300" gradientUnits="userSpaceOnUse">
              <stop offset="0%" stopColor="#D5FF6E" stopOpacity="0.85" />
              <stop offset="35%" stopColor="#9BE34A" stopOpacity="0.6" />
              <stop offset="70%" stopColor="#5EA832" stopOpacity="0.15" />
              <stop offset="100%" stopColor="#D5FF6E" stopOpacity="0.8" />
            </linearGradient>
            <linearGradient id="silk-grad-2" x1="300" y1="20" x2="20" y2="300" gradientUnits="userSpaceOnUse">
              <stop offset="0%" stopColor="#9BE34A" stopOpacity="0.75" />
              <stop offset="50%" stopColor="#C5FF67" stopOpacity="0.3" />
              <stop offset="100%" stopColor="#5EA832" stopOpacity="0.7" />
            </linearGradient>
          </defs>

          {/* Multiple parallel wave contours creating the silk fabric aura */}
          <path
            d="M 160 22 C 245 22, 298 85, 298 160 C 298 235, 235 298, 160 298 C 85 298, 22 235, 22 160 C 22 95, 75 22, 160 22 Z"
            stroke="url(#silk-grad-1)"
            strokeWidth="1.8"
            strokeDasharray="300 25"
            opacity="0.9"
          />
          <path
            d="M 160 38 C 235 18, 292 102, 282 170 C 272 238, 212 288, 145 282 C 78 276, 28 208, 38 138 C 48 68, 108 48, 160 38 Z"
            stroke="url(#silk-grad-2)"
            strokeWidth="1.4"
            opacity="0.65"
          />
          <path
            d="M 160 52 C 225 38, 272 112, 262 175 C 252 228, 198 272, 140 264 C 88 256, 52 198, 60 145 C 68 92, 118 60, 160 52 Z"
            stroke="url(#silk-grad-1)"
            strokeWidth="1.2"
            opacity="0.55"
          />
        </svg>

        {/* Counter-rotating wave ribbons (Counter-Clockwise) */}
        <svg
          className="absolute inset-0 w-full h-full animate-swirl-ccw pointer-events-none opacity-60"
          viewBox="0 0 320 320"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M 160 30 Q 275 75 288 160 Q 265 255 160 288 Q 55 255 32 160 Q 55 55 160 30 Z"
            stroke="#9BE34A"
            strokeWidth="1.2"
            strokeDasharray="180 35"
          />
        </svg>

        {/* Deep Translucent Glass Sphere */}
        <div className="relative w-56 h-56 lg:w-60 lg:h-60 rounded-full bg-[#050D07]/85 backdrop-blur-md border border-[rgba(155,227,74,0.35)] shadow-orbit-core flex flex-col items-center justify-center p-4 text-center">
          {/* Logo at center */}
          <div className="mb-2">
            <OrbitLogo size={42} glow={true} />
          </div>

          {/* Title: Personal Agent */}
          <h1 className="text-xl lg:text-2xl font-bold tracking-tight text-white drop-shadow-[0_2px_8px_rgba(0,0,0,0.8)]">
            Personal Agent
          </h1>

          {/* Subtitle: Plan • Code • Automate • Execute */}
          <p className="mt-1 text-[11px] lg:text-xs font-medium text-[#A4B5A3] tracking-wide flex items-center justify-center gap-1.5">
            <span>Plan</span>
            <span className="text-[#9BE34A] opacity-90">•</span>
            <span>Code</span>
            <span className="text-[#9BE34A] opacity-90">•</span>
            <span>Automate</span>
            <span className="text-[#9BE34A] opacity-90">•</span>
            <span>Execute</span>
          </p>
        </div>
      </div>
    </div>
  );
};
