import React from "react";

interface OrbitLogoProps {
  className?: string;
  size?: number;
  glow?: boolean;
}

export const OrbitLogo: React.FC<OrbitLogoProps> = ({
  className = "",
  size = 32,
  glow = true,
}) => {
  return (
    <div
      className={`relative inline-flex items-center justify-center shrink-0 ${className}`}
      style={{ width: size, height: size }}
    >
      {glow && (
        <div
          className="absolute inset-0 rounded-full blur-md opacity-70 pointer-events-none"
          style={{
            background:
              "radial-gradient(circle, rgba(155, 227, 74, 0.45) 0%, rgba(155, 227, 74, 0) 70%)",
          }}
        />
      )}
      <svg
        width={size}
        height={size}
        viewBox="0 0 48 48"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="relative z-10"
      >
        <defs>
          <linearGradient id="orbit-logo-grad" x1="6" y1="42" x2="42" y2="6" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#66B83D" />
            <stop offset="50%" stopColor="#9BE34A" />
            <stop offset="100%" stopColor="#C5FF67" />
          </linearGradient>
          <filter id="logo-glow" x="-20%" y="-20%" width="140%" height="140%">
            <feDropShadow dx="0" dy="0" stdDeviation="2.5" floodColor="#9BE34A" floodOpacity="0.6" />
          </filter>
        </defs>
        {/* Modern organic loop/leaf icon from reference */}
        <path
          d="M12 28C9 23 10 14 17 9C23 5 33 6 39 12C43 16 43 24 37 31C31 38 22 41 15 39C10 38 13 32 17 29C23 25 31 22 34 17C35 15 32 12 28 12C21 12 15 18 13 24C12 26 12 27 12 28Z"
          stroke="url(#orbit-logo-grad)"
          strokeWidth="3.6"
          strokeLinecap="round"
          strokeLinejoin="round"
          filter="url(#logo-glow)"
        />
      </svg>
    </div>
  );
};
