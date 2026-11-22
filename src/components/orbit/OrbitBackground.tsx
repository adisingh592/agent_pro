import React from "react";

export const OrbitBackground: React.FC = () => {
  return (
    <div className="absolute inset-0 pointer-events-none select-none z-0 overflow-hidden">
      {/* Deep forest base tone */}
      <div className="absolute inset-0 bg-[#050907]" />

      {/* Real atmospheric mountain & misty pine forest landscape */}
      <img
        src="/orbit-scene.jpg"
        alt="Orbit Environment"
        className="absolute inset-0 w-full h-full object-cover opacity-80 pointer-events-none"
      />

      {/* Gradient vignette overlays to ensure perfect contrast and depth */}
      <div className="absolute inset-0 bg-gradient-to-t from-[#050907] via-transparent to-[#050907]/70" />
      <div className="absolute inset-0 bg-radial from-transparent via-[#050907]/20 to-[#050907]/80" />

      {/* Center atmospheric green volumetric aura behind core */}
      <div
        className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[680px] h-[680px] rounded-full blur-[130px] opacity-45 pointer-events-none"
        style={{
          background: "radial-gradient(circle, rgba(155, 227, 74, 0.45) 0%, rgba(30, 70, 35, 0.15) 50%, transparent 75%)",
        }}
      />

      {/* Neon emerald underglow radiating beneath the command bar onto the valley */}
      <div
        className="absolute bottom-16 left-1/2 -translate-x-1/2 w-[540px] h-[36px] rounded-full blur-[24px] opacity-80 pointer-events-none"
        style={{
          background: "radial-gradient(ellipse at center, #9BE34A 0%, rgba(155, 227, 74, 0.6) 45%, transparent 80%)",
        }}
      />

      {/* Diffuse misty glow in the lower valley */}
      <div
        className="absolute -bottom-10 left-1/2 -translate-x-1/2 w-[750px] h-[140px] rounded-full blur-[60px] opacity-40 pointer-events-none"
        style={{
          background: "radial-gradient(ellipse at center, rgba(155, 227, 74, 0.5) 0%, rgba(50, 120, 40, 0.2) 60%, transparent 85%)",
        }}
      />
    </div>
  );
};
