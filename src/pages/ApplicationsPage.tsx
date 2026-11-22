import React, { useState } from "react";
import {
  LayoutGrid,
  Search,
  Play,
  CheckCircle,
  ExternalLink,
  Layers,
  Sparkles
} from "lucide-react";
import { mockInstalledApps } from "../lib/mockData";
import { InstalledApp } from "../types/agent";

export const ApplicationsPage: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState<string>("All");
  const [stagedApp, setStagedApp] = useState<InstalledApp | null>(null);

  const categories = ["All", "Browser", "Development", "Productivity", "System", "Media"];

  const filteredApps = mockInstalledApps.filter((app) => {
    const matchesSearch = app.name.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = selectedCategory === "All" || app.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  return (
    <div className="flex-1 flex flex-col h-full overflow-hidden p-6 space-y-5">
      {/* Page Header */}
      <div className="flex items-center justify-between pb-4 border-b border-border-subtle shrink-0">
        <div>
          <h1 className="text-lg font-semibold text-text-primary tracking-tight flex items-center gap-2">
            <LayoutGrid className="w-5 h-5 text-accent" />
            Applications Management
          </h1>
          <p className="text-xs text-text-muted mt-0.5">
            Discover, monitor, and launch verified desktop applications through controlled safe tools.
          </p>
        </div>
      </div>

      {/* Filter & Search Bar */}
      <div className="flex flex-col sm:flex-row gap-3 shrink-0">
        <div className="relative flex-1">
          <Search className="w-3.5 h-3.5 text-text-muted absolute left-3 top-2.5" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search installed applications..."
            className="w-full h-8 bg-bg-secondary border border-border-subtle rounded-md pl-8 pr-3 text-xs text-text-primary placeholder:text-text-muted focus:border-accent/60 outline-none"
          />
        </div>

        {/* Category Filter Pills */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1">
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`px-2.5 py-1 rounded text-xs font-medium whitespace-nowrap transition-colors ${
                selectedCategory === cat
                  ? "bg-accent text-bg-main font-semibold"
                  : "bg-bg-secondary text-text-secondary hover:text-text-primary border border-border-subtle"
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {/* Confirmation Staging Banner */}
      {stagedApp && (
        <div className="p-3 rounded-lg bg-bg-elevated border border-accent/40 flex items-center justify-between text-xs shrink-0">
          <div className="flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-accent" />
            <span>
              Action Staged: Launch <strong>{stagedApp.name}</strong>? Requires explicit user approval.
            </span>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => {
                alert(`Approved: Simulated launch of ${stagedApp.name}.`);
                setStagedApp(null);
              }}
              className="px-2.5 py-1 rounded bg-accent hover:bg-accent-hover text-bg-main font-semibold text-xs"
            >
              Approve & Launch
            </button>
            <button
              onClick={() => setStagedApp(null)}
              className="px-2.5 py-1 rounded bg-bg-hover text-text-secondary text-xs"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Applications Grid */}
      <div className="flex-1 overflow-y-auto">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {filteredApps.map((app) => (
            <div
              key={app.id}
              className="p-3.5 rounded-lg bg-bg-secondary border border-border-subtle hover:border-border-hover transition-all flex flex-col justify-between space-y-3 group"
            >
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="text-xs font-semibold text-text-primary group-hover:text-accent transition-colors">
                    {app.name}
                  </h3>
                  <span className="text-[10px] text-text-muted px-1.5 py-0.5 rounded bg-bg-elevated border border-border-subtle/50 mt-1 inline-block">
                    {app.category}
                  </span>
                </div>

                <div className="flex items-center gap-1.5 text-[11px]">
                  {app.isRunning ? (
                    <span className="flex items-center gap-1 text-status-success font-medium">
                      <span className="w-1.5 h-1.5 rounded-full bg-status-success animate-pulse" />
                      Running (PID {app.pid})
                    </span>
                  ) : (
                    <span className="text-text-muted">Offline</span>
                  )}
                </div>
              </div>

              <div className="font-mono text-[10px] text-text-muted truncate bg-bg-main p-1 rounded border border-border-subtle/30">
                {app.executablePath}
              </div>

              <div className="flex items-center justify-between pt-1 border-t border-border-subtle/40 text-xs">
                <span className="text-[10px] text-text-muted">
                  {app.lastOpened ? `Last opened: ${app.lastOpened}` : "Installed"}
                </span>

                <button
                  onClick={() => setStagedApp(app)}
                  className="flex items-center gap-1 px-2.5 py-1 rounded bg-bg-elevated hover:bg-accent hover:text-bg-main text-text-secondary text-xs font-medium transition-all"
                >
                  <Play className="w-3 h-3" />
                  <span>Launch</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
