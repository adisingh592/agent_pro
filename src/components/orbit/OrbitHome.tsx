import React from "react";
import { OrbitHeader } from "./OrbitHeader";
import { OrbitBackground } from "./OrbitBackground";
import { OrbitPaths } from "./OrbitPaths";
import { OrbitCore } from "./OrbitCore";
import { NavigationPanel } from "./NavigationPanel";
import { CommandInput } from "./CommandInput";
import { NavPage } from "../../types/agent";
import { Code2, Layers, LayoutGrid, Zap, Clock, Settings } from "lucide-react";

interface OrbitHomeProps {
  onNavigate: (page: NavPage) => void;
  onStartChat: (prompt: string) => void;
  modelName?: string;
  onModelSelect?: (model: string) => void;
}

export const OrbitHome: React.FC<OrbitHomeProps> = ({
  onNavigate,
  onStartChat,
  modelName = "Qwen3 8B",
  onModelSelect,
}) => {
  return (
    <div className="relative w-screen h-screen overflow-hidden flex flex-col justify-between bg-[#050907] text-[#F1F5ED] select-none">
      {/* 1. Atmospheric Mountain Landscape & Star Background */}
      <OrbitBackground />

      {/* 2. Concentric Orbital Paths & 8 Glowing Nodes */}
      <OrbitPaths />

      {/* 3. Top Minimal Transparent Bar */}
      <OrbitHeader
        modelName={modelName}
        onModelSelect={onModelSelect}
        onNavigateHome={() => onNavigate("orbit")}
        onNavigate={onNavigate}
        currentPage="orbit"
      />

      {/* 4. Center Spatial Playground (Core + 6 Floating Curved Navigation Cards) */}
      <main className="relative z-20 flex-1 flex items-center justify-center px-4 sm:px-8 py-2">
        <div className="w-full max-w-6xl flex items-center justify-between">
          {/* Left Column of Floating Cards (Curved along orbital ring) */}
          <div className="flex flex-col gap-6 md:gap-7 items-end">
            {/* Top-Left: IDE */}
            <div className="translate-x-3 md:translate-x-6">
              <NavigationPanel
                id="panel-ide"
                title="IDE"
                subtitleLine1="Code, run and build"
                subtitleLine2="with your agent"
                icon={Code2}
                onClick={() => onNavigate("ide")}
              />
            </div>

            {/* Mid-Left: Agent */}
            <div className="translate-x-0">
              <NavigationPanel
                id="panel-agent"
                title="Agent"
                subtitleLine1="Autonomous tasks,"
                subtitleLine2="planning and execution"
                icon={Layers}
                onClick={() => onNavigate("computer")}
              />
            </div>

            {/* Bottom-Left: Skills */}
            <div className="translate-x-3 md:translate-x-6">
              <NavigationPanel
                id="panel-skills"
                title="Skills"
                subtitleLine1="Tools, integrations"
                subtitleLine2="and capabilities"
                icon={LayoutGrid}
                onClick={() => onNavigate("skills")}
              />
            </div>
          </div>

          {/* Central Luminous AI Core */}
          <div className="mx-2 md:mx-6 shrink-0">
            <OrbitCore />
          </div>

          {/* Right Column of Floating Cards (Curved along orbital ring) */}
          <div className="flex flex-col gap-6 md:gap-7 items-start">
            {/* Top-Right: Automation */}
            <div className="-translate-x-3 md:-translate-x-6">
              <NavigationPanel
                id="panel-automation"
                title="Automation"
                subtitleLine1="Create and run"
                subtitleLine2="automated workflows"
                icon={Zap}
                onClick={() => onNavigate("automation")}
              />
            </div>

            {/* Mid-Right: History */}
            <div className="translate-x-0">
              <NavigationPanel
                id="panel-history"
                title="History"
                subtitleLine1="Conversations, actions"
                subtitleLine2="and past executions"
                icon={Clock}
                onClick={() => onNavigate("activity")}
              />
            </div>

            {/* Bottom-Right: Settings */}
            <div className="-translate-x-3 md:-translate-x-6">
              <NavigationPanel
                id="panel-settings"
                title="Settings"
                subtitleLine1="Models, permissions"
                subtitleLine2="and system configuration"
                icon={Settings}
                onClick={() => onNavigate("settings")}
              />
            </div>
          </div>
        </div>
      </main>

      {/* 5. Bottom Floating Command Bar with Backlight */}
      <footer className="relative z-30 pb-7 pt-2 flex items-center justify-center px-4">
        <CommandInput
          onSubmit={(prompt) => {
            onStartChat(prompt);
          }}
          placeholder="Ask anything, or tell me what to do..."
        />
      </footer>
    </div>
  );
};
