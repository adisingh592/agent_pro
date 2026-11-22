import React from "react";

export const OrbitBackground: React.FC = () => {
  return (
    <div className="absolute inset-0 pointer-events-none overflow-hidden select-none z-0">
      {/* Deep forest base tone */}
      <div className="absolute inset-0 bg-[#050907]" />

      {/* Atmospheric center radial glow (ambient green volumetric aura) */}
      <div
        className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[700px] rounded-full blur-[140px] opacity-35"
        style={{
          background: "radial-gradient(circle, rgba(155, 227, 74, 0.4) 0%, rgba(30, 70, 35, 0.15) 50%, transparent 75%)",
        }}
      />

      {/* Lower volumetric glow behind the bottom command bar */}
      <div
        className="absolute -bottom-20 left-1/2 -translate-x-1/2 w-[650px] h-[220px] rounded-full blur-[80px] opacity-45"
        style={{
          background: "radial-gradient(ellipse at center, rgba(155, 227, 74, 0.6) 0%, rgba(100, 180, 50, 0.2) 50%, transparent 80%)",
        }}
      />

      {/* Upper subtle aurora light */}
      <div
        className="absolute -top-32 left-1/2 -translate-x-1/2 w-[900px] h-[350px] rounded-full blur-[160px] opacity-20"
        style={{
          background: "radial-gradient(ellipse at center, rgba(100, 180, 60, 0.3) 0%, transparent 70%)",
        }}
      />

      {/* Starry night subtle particles / sparks */}
      <div className="absolute inset-0 opacity-40">
        <div className="absolute top-[18%] left-[12%] w-1 h-1 rounded-full bg-[#C5FF67] animate-twinkle" />
        <div className="absolute top-[28%] left-[24%] w-1.5 h-1.5 rounded-full bg-[#9BE34A] animate-twinkle [animation-delay:1.2s]" />
        <div className="absolute top-[14%] right-[22%] w-1 h-1 rounded-full bg-[#C5FF67] animate-twinkle [animation-delay:0.7s]" />
        <div className="absolute top-[32%] right-[14%] w-1.5 h-1.5 rounded-full bg-[#9BE34A] animate-twinkle [animation-delay:2.1s]" />
        <div className="absolute top-[48%] left-[8%] w-1 h-1 rounded-full bg-[#C5FF67] opacity-60" />
        <div className="absolute top-[52%] right-[9%] w-1 h-1 rounded-full bg-[#C5FF67] opacity-60" />
        <div className="absolute top-[72%] left-[18%] w-1 h-1 rounded-full bg-[#9BE34A] opacity-40" />
        <div className="absolute top-[68%] right-[20%] w-1 h-1 rounded-full bg-[#9BE34A] opacity-40" />
      </div>

      {/* Layered mountain ridges and pine tree silhouettes at bottom left and bottom right */}
      <svg
        className="absolute bottom-0 left-0 w-full h-[360px] object-cover pointer-events-none"
        viewBox="0 0 1440 360"
        fill="none"
        preserveAspectRatio="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <defs>
          <linearGradient id="mountains-far" x1="720" y1="120" x2="720" y2="360" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#0B1C10" stopOpacity="0.6" />
            <stop offset="100%" stopColor="#060C08" stopOpacity="0.9" />
          </linearGradient>
          <linearGradient id="mountains-mid" x1="720" y1="180" x2="720" y2="360" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#08140B" stopOpacity="0.85" />
            <stop offset="100%" stopColor="#040805" />
          </linearGradient>
          <linearGradient id="forest-fore" x1="720" y1="240" x2="720" y2="360" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#060E08" />
            <stop offset="100%" stopColor="#020403" />
          </linearGradient>
        </defs>

        {/* Far Distant Mountain Ridges */}
        <path
          d="M0 240 Q180 150 360 200 T720 230 T1080 170 T1440 220 L1440 360 L0 360 Z"
          fill="url(#mountains-far)"
        />

        {/* Left Mountain Peak with Deep Valleys */}
        <path
          d="M0 160 Q120 180 220 240 T440 280 L0 360 Z"
          fill="url(#mountains-mid)"
        />

        {/* Right Mountain Peak */}
        <path
          d="M1440 150 Q1300 200 1180 250 T960 290 L1440 360 Z"
          fill="url(#mountains-mid)"
        />

        {/* Detailed Forest Silhouettes (Pine Trees on Left) */}
        <path
          d="M0 240 L15 230 L30 242 L42 225 L55 240 L70 218 L85 245 L105 232 L120 250 L140 228 L160 255 L190 240 L220 268 L250 255 L280 275 L320 285 L360 300 L400 310 L440 330 L480 345 L0 360 Z"
          fill="url(#forest-fore)"
        />

        {/* Detailed Forest Silhouettes (Pine Trees on Right) */}
        <path
          d="M1440 230 L1420 215 L1405 235 L1385 220 L1370 240 L1345 225 L1330 248 L1300 235 L1280 255 L1250 245 L1220 268 L1180 260 L1150 280 L1100 295 L1050 310 L1000 325 L950 345 L1440 360 Z"
          fill="url(#forest-fore)"
        />

        {/* Center Horizon valley ground gradient overlay */}
        <rect x="0" y="320" width="1440" height="40" fill="#040705" />
      </svg>
    </div>
  );
};
