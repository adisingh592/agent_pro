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
          className="absolute inset-0 rounded-full blur-md opacity-75 pointer-events-none"
          style={{
            background:
              "radial-gradient(circle, rgba(155, 227, 74, 0.5) 0%, rgba(155, 227, 74, 0) 70%)",
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
          <linearGradient id="orbit-logo-grad" x1="8" y1="40" x2="40" y2="8" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#5EA832" />
            <stop offset="50%" stopColor="#9BE34A" />
            <stop offset="100%" stopColor="#D5FF6E" />
          </linearGradient>
          <filter id="logo-glow-filter" x="-25%" y="-25%" width="150%" height="150%">
            <feDropShadow dx="0" dy="0" stdDeviation="2.5" floodColor="#9BE34A" floodOpacity="0.7" />
          </filter>
        </defs>
        {/* Exact tilted organic ribbon/leaf loop from reference image */}
        <path
          d="M 14 30 C 9 24 10 15 17 10 C 23 5 33 6 39 12 C 44 17 44 26 37 32 C 30 39 20 41 14 38 C 11 36 13 31 17 29 C 23 26 31 22 34 17 C 35 15 32 12 28 12 C 21 12 16 19 14 25 Z"
          stroke="url(#orbit-logo-grad)"
          strokeWidth="3.6"
          strokeLinecap="round"
          strokeLinejoin="round"
          filter="url(#logo-glow-filter)"
        />
      </svg>
    </div>
  );
};
