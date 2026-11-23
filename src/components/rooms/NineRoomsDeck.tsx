import React from "react";
import { NavPage } from "../../types/agent";
import { Search, Home, ArrowUpRight, Sparkles, Orbit } from "lucide-react";

interface NineRoomsDeckProps {
  onNavigate: (page: NavPage) => void;
}

interface RoomItem {
  id: string;
  num: string;
  title: string;
  badge: string;
  desc: string;
  thumb: string;
  url: string;
}

const ROOMS: RoomItem[] = [
  {
    id: "overview",
    num: "01",
    title: "Overview",
    badge: "today",
    desc: "Spend, live ledger, fleet health",
    thumb: "/templates/aurora/assets/img/thumbs/overview.jpg",
    url: "/templates/aurora/overview.html",
  },
  {
    id: "tasks",
    num: "02",
    title: "Tasks",
    badge: "12",
    desc: "Plans, revisions, steps and artifacts",
    thumb: "/templates/aurora/assets/img/thumbs/tasks.jpg",
    url: "/templates/aurora/tasks.html",
  },
  {
    id: "operations",
    num: "03",
    title: "Operations",
    badge: "2 live",
    desc: "Queue, workers, throughput, errors",
    thumb: "/templates/aurora/assets/img/thumbs/operations.jpg",
    url: "/templates/aurora/operations.html",
  },
  {
    id: "local-chat",
    num: "04",
    title: "Local chat",
    badge: "qwen3",
    desc: "Talk to on-device models, $0 per token",
    thumb: "/templates/aurora/assets/img/thumbs/local-chat.jpg",
    url: "/templates/aurora/local-chat.html",
  },
  {
    id: "fine-tuning",
    num: "05",
    title: "Fine-tuning",
    badge: "1 run",
    desc: "Datasets, runs and LoRA adapters",
    thumb: "/templates/aurora/assets/img/thumbs/fine-tuning.jpg",
    url: "/templates/aurora/fine-tuning.html",
  },
  {
    id: "scheduled",
    num: "06",
    title: "Scheduled work",
    badge: "6 jobs",
    desc: "Cron jobs on a 24 h timeline",
    thumb: "/templates/aurora/assets/img/thumbs/scheduled.jpg",
    url: "/templates/aurora/scheduled.html",
  },
  {
    id: "memory",
    num: "07",
    title: "Long-term memory",
    badge: "2 148",
    desc: "Facts, runbooks, hosts and files",
    thumb: "/templates/aurora/assets/img/thumbs/memory.jpg",
    url: "/templates/aurora/memory.html",
  },
  {
    id: "integrations",
    num: "08",
    title: "Integrations",
    badge: "12/16",
    desc: "Connected tools, local models & APIs",
    thumb: "/templates/aurora/assets/img/thumbs/integrations.jpg",
    url: "/templates/aurora/integrations.html",
  },
  {
    id: "audit",
    num: "09",
    title: "Audit trail",
    badge: "318",
    desc: "Every action, signed and chained",
    thumb: "/templates/aurora/assets/img/thumbs/audit.jpg",
    url: "/templates/aurora/audit.html",
  },
  {
    id: "ui-kit",
    num: "··",
    title: "UI kit",
    badge: "kit",
    desc: "Every component and state",
    thumb: "/templates/aurora/assets/img/thumbs/ui-kit.jpg",
    url: "/templates/aurora/ui-kit.html",
  },
];

export const NineRoomsDeck: React.FC<NineRoomsDeckProps> = ({ onNavigate }) => {
  const handleRoomClick = (room: RoomItem) => {
    // Open the Aurora room
    window.location.href = room.url;
  };

  return (
    <div className="relative w-screen h-screen overflow-hidden flex flex-col justify-between bg-[#04060E] text-[#EEF0FF] select-none font-sans">
      {/* Background radial atmosphere */}
      <div 
        className="absolute inset-0 pointer-events-none z-0 opacity-80"
        style={{
          background: `
            radial-gradient(65% 55% at 50% 10%, rgba(30, 45, 90, 0.45), transparent 70%),
            radial-gradient(50% 45% at 20% 90%, rgba(109, 74, 255, 0.2), transparent 60%),
            radial-gradient(40% 40% at 85% 85%, rgba(139, 233, 255, 0.15), transparent 60%),
            linear-gradient(180deg, #04060E 0%, #070A18 100%)
          `,
        }}
      />
      {/* Subtle coordinate grid overlay */}
      <div 
        className="absolute inset-0 pointer-events-none z-0 opacity-15"
        style={{
          backgroundImage: "linear-gradient(rgba(255,255,255,.05) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,.05) 1px, transparent 1px)",
          backgroundSize: "48px 48px",
          maskImage: "radial-gradient(75% 65% at 50% 45%, #000, transparent)",
          WebkitMaskImage: "radial-gradient(75% 65% at 50% 45%, #000, transparent)",
        }}
      />

      {/* Top Header */}
      <header className="relative z-30 w-full px-8 pt-5 pb-3 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <h1 className="text-xl md:text-2xl font-light tracking-tight text-white flex items-center gap-2">
            <span>Nine</span>
            <span className="text-[#FFB36B] font-normal">rooms</span>
          </h1>

          {/* Quick switcher between Orbit Core & Nine Rooms */}
          <div className="flex items-center p-0.5 rounded-full bg-white/5 border border-white/10 ml-4 backdrop-blur-md">
            <button
              onClick={() => onNavigate("orbit")}
              className="flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium text-white/70 hover:text-white hover:bg-white/10 transition-all cursor-pointer"
            >
              <Orbit className="w-3.5 h-3.5 text-[#9BE34A]" />
              <span>Orbit Core</span>
            </button>
            <button
              onClick={() => onNavigate("rooms")}
              className="flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-white/15 text-white shadow-sm border border-white/10 cursor-pointer"
            >
              <Sparkles className="w-3.5 h-3.5 text-[#8BE9FF]" />
              <span>Nine Rooms</span>
            </button>
          </div>
        </div>

        <div className="text-[11px] font-mono tracking-[0.25em] text-[#8BE9FF]/80 uppercase font-medium">
          CLICK A WINDOW TO FLY THERE ↗
        </div>
      </header>

      {/* Main Grid: 2 rows of 5 cards */}
      <main className="relative z-20 flex-1 px-8 py-2 overflow-y-auto max-h-[calc(100vh-140px)] flex items-center">
        <div className="w-full max-w-7xl mx-auto grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3.5 md:gap-4">
          {ROOMS.map((room) => (
            <article
              key={room.id}
              onClick={() => handleRoomClick(room)}
              className="group relative flex flex-col rounded-2xl border border-white/10 hover:border-[#8BE9FF]/50 bg-[#0B1024]/70 hover:bg-[#121A3B]/85 backdrop-blur-xl overflow-hidden cursor-pointer transition-all duration-300 hover:-translate-y-1 hover:shadow-[0_16px_36px_rgba(4,6,14,0.8),0_0_24px_rgba(139,233,255,0.2)]"
            >
              {/* Thumbnail Container */}
              <div className="relative aspect-[16/10] w-full overflow-hidden bg-black/40 border-b border-white/5">
                <img
                  src={room.thumb}
                  alt={room.title}
                  className="w-full h-full object-cover object-top opacity-85 group-hover:opacity-100 group-hover:scale-105 transition-all duration-500"
                  onError={(e) => {
                    // Fallback to high tech gradient if image is loading
                    (e.target as HTMLElement).style.display = "none";
                  }}
                />
                <div className="absolute inset-0 bg-gradient-to-t from-[#0B1024] via-transparent to-transparent opacity-60" />

                {/* Flying indicator icon on hover */}
                <div className="absolute top-2.5 right-2.5 w-6 h-6 rounded-full bg-black/60 border border-white/15 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                  <ArrowUpRight className="w-3.5 h-3.5 text-[#8BE9FF]" />
                </div>
              </div>

              {/* Card Meta Content */}
              <div className="p-3.5 flex flex-col justify-between flex-1 gap-1.5">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-1.5">
                    <span className="font-mono text-xs font-semibold text-[#8BE9FF]">
                      {room.num}
                    </span>
                    <h2 className="text-sm font-semibold tracking-tight text-white group-hover:text-[#8BE9FF] transition-colors">
                      {room.title}
                    </h2>
                  </div>
                  <span className="text-[11px] font-mono px-1.5 py-0.5 rounded bg-white/5 border border-white/10 text-white/70">
                    {room.badge}
                  </span>
                </div>
                <p className="text-[11px] text-white/55 line-clamp-1 leading-relaxed">
                  {room.desc}
                </p>
              </div>
            </article>
          ))}
        </div>
      </main>

      {/* Floating Bottom Navigation Dock */}
      <footer className="relative z-30 pb-5 pt-1 flex items-center justify-center">
        <div className="flex items-center gap-2 p-1.5 px-3 rounded-full bg-[#0E142B]/90 border border-white/15 backdrop-blur-2xl shadow-[0_12px_40px_rgba(0,0,0,0.6)]">
          {/* Blue Sphere Icon */}
          <div className="w-7 h-7 rounded-full bg-gradient-to-tr from-[#3B82F6] to-[#8BE9FF] shadow-[0_0_12px_rgba(139,233,255,0.7)] flex items-center justify-center">
            <div className="w-3 h-3 rounded-full bg-white/60 blur-[1px]" />
          </div>

          <div className="flex flex-col px-1.5">
            <span className="text-[9px] font-mono tracking-widest text-[#8BE9FF]/70 uppercase font-semibold">
              ROOMS · PRESS G
            </span>
            <span className="text-xs font-bold text-white tracking-wide">
              Control Deck
            </span>
          </div>

          <div className="h-4 w-px bg-white/15 mx-1" />

          {/* Home button (switches to Orbit Core) */}
          <button
            onClick={() => onNavigate("orbit")}
            className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-white/10 hover:bg-[#9BE34A]/20 hover:border-[#9BE34A]/40 border border-transparent text-xs font-medium text-white transition-all cursor-pointer"
          >
            <Home className="w-3.5 h-3.5 text-[#9BE34A]" />
            <span>Orbit Home</span>
          </button>

          {/* Search Button */}
          <button
            onClick={() => {
              // Trigger palette or overview
              window.location.href = "/templates/aurora/overview.html";
            }}
            title="Search command palette"
            className="w-7 h-7 rounded-full bg-white/5 hover:bg-white/15 border border-white/10 flex items-center justify-center text-white/70 hover:text-white transition-all cursor-pointer"
          >
            <Search className="w-3.5 h-3.5" />
          </button>
        </div>
      </footer>
    </div>
  );
};
