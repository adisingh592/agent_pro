import React from "react";

export const OrbitPaths: React.FC = () => {
  return (
    <div className="absolute inset-0 pointer-events-none z-10 flex items-center justify-center select-none">
      <svg
        className="w-[1020px] h-[660px] max-w-full max-h-full overflow-visible"
        viewBox="0 0 1020 660"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <defs>
          <linearGradient id="orbit-stroke-outer" x1="0" y1="0" x2="1020" y2="660" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#9BE34A" stopOpacity="0.25" />
            <stop offset="25%" stopColor="#9BE34A" stopOpacity="0.65" />
            <stop offset="50%" stopColor="#C5FF67" stopOpacity="0.3" />
            <stop offset="75%" stopColor="#9BE34A" stopOpacity="0.7" />
            <stop offset="100%" stopColor="#5EA832" stopOpacity="0.25" />
          </linearGradient>
          <linearGradient id="orbit-stroke-mid" x1="160" y1="120" x2="860" y2="540" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#9BE34A" stopOpacity="0.45" />
            <stop offset="50%" stopColor="#9BE34A" stopOpacity="0.15" />
            <stop offset="100%" stopColor="#9BE34A" stopOpacity="0.45" />
          </linearGradient>
          <filter id="node-glow-filter" x="-60%" y="-60%" width="220%" height="220%">
            <feDropShadow dx="0" dy="0" stdDeviation="4" floodColor="#C5FF67" floodOpacity="0.9" />
            <feDropShadow dx="0" dy="0" stdDeviation="8" floodColor="#9BE34A" floodOpacity="0.6" />
          </filter>
        </defs>

        {/* Innermost subtle dashed circular ring */}
        <circle
          cx="510"
          cy="330"
          r="195"
          stroke="url(#orbit-stroke-mid)"
          strokeWidth="1.2"
          strokeDasharray="4 6"
          opacity="0.6"
        />

        {/* Middle ellipse ring */}
        <ellipse
          cx="510"
          cy="330"
          rx="265"
          ry="220"
          stroke="url(#orbit-stroke-mid)"
          strokeWidth="1"
          opacity="0.75"
        />

        {/* Primary outer orbital ring passing behind the 6 cards */}
        <ellipse
          cx="510"
          cy="330"
          rx="335"
          ry="250"
          stroke="url(#orbit-stroke-outer)"
          strokeWidth="1.6"
          opacity="0.85"
        />

        {/* Outermost faint guide ring */}
        <ellipse
          cx="510"
          cy="330"
          rx="380"
          ry="275"
          stroke="#9BE34A"
          strokeWidth="0.8"
          strokeDasharray="3 9"
          opacity="0.3"
        />

        {/* 8 Distinct Luminous Orbital Nodes matching reference image */}
        {/* 1. Top Node (12 o'clock: between IDE and Automation) */}
        <g filter="url(#node-glow-filter)">
          <circle cx="510" cy="80" r="4.5" fill="#C5FF67" />
          <circle cx="510" cy="80" r="9" stroke="#9BE34A" strokeWidth="1" opacity="0.65" />
        </g>

        {/* 2. Top-Left Node (between IDE and Agent) */}
        <g filter="url(#node-glow-filter)">
          <circle cx="270" cy="155" r="4.5" fill="#C5FF67" />
          <circle cx="270" cy="155" r="9" stroke="#9BE34A" strokeWidth="1" opacity="0.65" />
        </g>

        {/* 3. Left Node (9 o'clock: near Agent card) */}
        <g filter="url(#node-glow-filter)">
          <circle cx="175" cy="330" r="4.5" fill="#C5FF67" />
          <circle cx="175" cy="330" r="9" stroke="#9BE34A" strokeWidth="1" opacity="0.65" />
        </g>

        {/* 4. Bottom-Left Node (between Agent and Skills) */}
        <g filter="url(#node-glow-filter)">
          <circle cx="270" cy="505" r="4.5" fill="#C5FF67" />
          <circle cx="270" cy="505" r="9" stroke="#9BE34A" strokeWidth="1" opacity="0.65" />
        </g>

        {/* 5. Bottom Node (6 o'clock: between Skills and Settings) */}
        <g filter="url(#node-glow-filter)">
          <circle cx="510" cy="580" r="4.5" fill="#C5FF67" />
          <circle cx="510" cy="580" r="9" stroke="#9BE34A" strokeWidth="1" opacity="0.65" />
        </g>

        {/* 6. Bottom-Right Node (between Settings and History) */}
        <g filter="url(#node-glow-filter)">
          <circle cx="750" cy="505" r="4.5" fill="#C5FF67" />
          <circle cx="750" cy="505" r="9" stroke="#9BE34A" strokeWidth="1" opacity="0.65" />
        </g>

        {/* 7. Right Node (3 o'clock: near History card) */}
        <g filter="url(#node-glow-filter)">
          <circle cx="845" cy="330" r="4.5" fill="#C5FF67" />
          <circle cx="845" cy="330" r="9" stroke="#9BE34A" strokeWidth="1" opacity="0.65" />
        </g>

        {/* 8. Top-Right Node (between Automation and History) */}
        <g filter="url(#node-glow-filter)">
          <circle cx="750" cy="155" r="4.5" fill="#C5FF67" />
          <circle cx="750" cy="155" r="9" stroke="#9BE34A" strokeWidth="1" opacity="0.65" />
        </g>
      </svg>
    </div>
  );
};
