import React from "react";

export const OrbitPaths: React.FC = () => {
  return (
    <div className="absolute inset-0 pointer-events-none z-10 flex items-center justify-center select-none">
      <svg
        className="w-[980px] h-[640px] max-w-full max-h-full overflow-visible"
        viewBox="0 0 980 640"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <defs>
          <linearGradient id="orbit-stroke-outer" x1="0" y1="0" x2="980" y2="640" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#9BE34A" stopOpacity="0.25" />
            <stop offset="25%" stopColor="#9BE34A" stopOpacity="0.55" />
            <stop offset="50%" stopColor="#C5FF67" stopOpacity="0.25" />
            <stop offset="75%" stopColor="#9BE34A" stopOpacity="0.6" />
            <stop offset="100%" stopColor="#66B83D" stopOpacity="0.2" />
          </linearGradient>
          <linearGradient id="orbit-stroke-mid" x1="140" y1="120" x2="840" y2="520" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#9BE34A" stopOpacity="0.4" />
            <stop offset="50%" stopColor="#9BE34A" stopOpacity="0.15" />
            <stop offset="100%" stopColor="#9BE34A" stopOpacity="0.35" />
          </linearGradient>
          <filter id="node-glow" x="-50%" y="-50%" width="200%" height="200%">
            <feDropShadow dx="0" dy="0" stdDeviation="4" floodColor="#C5FF67" floodOpacity="0.8" />
            <feDropShadow dx="0" dy="0" stdDeviation="8" floodColor="#9BE34A" floodOpacity="0.5" />
          </filter>
        </defs>

        {/* Innermost subtle dashed circular ring */}
        <circle
          cx="490"
          cy="320"
          r="190"
          stroke="url(#orbit-stroke-mid)"
          strokeWidth="1.2"
          strokeDasharray="4 6"
          opacity="0.6"
        />

        {/* Middle ellipse ring */}
        <ellipse
          cx="490"
          cy="320"
          rx="250"
          ry="210"
          stroke="url(#orbit-stroke-mid)"
          strokeWidth="1"
          opacity="0.75"
        />

        {/* Outer primary orbital ring spanning behind the 6 floating cards */}
        <ellipse
          cx="490"
          cy="320"
          rx="320"
          ry="240"
          stroke="url(#orbit-stroke-outer)"
          strokeWidth="1.5"
          opacity="0.8"
        />

        {/* Outermost faint guide ring */}
        <ellipse
          cx="490"
          cy="320"
          rx="360"
          ry="260"
          stroke="#9BE34A"
          strokeWidth="0.8"
          strokeDasharray="2 8"
          opacity="0.3"
        />

        {/* 4 Luminous Orbital Nodes positioned on the primary outer ring */}
        {/* 1. Top Orbital Node (at 12 o'clock: x=490, y=320 - 240 = 80) */}
        <g filter="url(#node-glow)">
          <circle cx="490" cy="80" r="5" fill="#C5FF67" />
          <circle cx="490" cy="80" r="10" stroke="#9BE34A" strokeWidth="1" opacity="0.6" />
        </g>

        {/* 2. Bottom Orbital Node (at 6 o'clock: x=490, y=320 + 240 = 560) */}
        <g filter="url(#node-glow)">
          <circle cx="490" cy="560" r="5" fill="#C5FF67" />
          <circle cx="490" cy="560" r="10" stroke="#9BE34A" strokeWidth="1" opacity="0.6" />
        </g>

        {/* 3. Left Orbital Node (at 9 o'clock: x=490 - 320 = 170, y=320) */}
        <g filter="url(#node-glow)">
          <circle cx="170" cy="320" r="5" fill="#C5FF67" />
          <circle cx="170" cy="320" r="10" stroke="#9BE34A" strokeWidth="1" opacity="0.6" />
        </g>

        {/* 4. Right Orbital Node (at 3 o'clock: x=490 + 320 = 810, y=320) */}
        <g filter="url(#node-glow)">
          <circle cx="810" cy="320" r="5" fill="#C5FF67" />
          <circle cx="810" cy="320" r="10" stroke="#9BE34A" strokeWidth="1" opacity="0.6" />
        </g>

        {/* Additional intermediate orbit spark nodes */}
        <circle cx="265" cy="150" r="2.5" fill="#9BE34A" opacity="0.7" />
        <circle cx="715" cy="150" r="2.5" fill="#9BE34A" opacity="0.7" />
        <circle cx="265" cy="490" r="2.5" fill="#9BE34A" opacity="0.7" />
        <circle cx="715" cy="490" r="2.5" fill="#9BE34A" opacity="0.7" />
      </svg>
    </div>
  );
};
