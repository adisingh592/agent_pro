import React, { useState } from "react";
import { Brain, Search, Plus, Tag, Calendar } from "lucide-react";
import { mockMemoryItems } from "../lib/mockData";
import { MemoryItem } from "../types/agent";

export const MemoryPage: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState<string>("all");
  const [memories, setMemories] = useState<MemoryItem[]>(mockMemoryItems);

  const categories = ["all", "preference", "workflow", "project", "system"];

  const filteredMemories = memories.filter((m) => {
    const matchesSearch =
      m.key.toLowerCase().includes(searchQuery.toLowerCase()) ||
      m.value.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCat = selectedCategory === "all" || m.category === selectedCategory;
    return matchesSearch && matchesCat;
  });

  return (
    <div className="flex-1 flex flex-col h-full overflow-hidden p-6 space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b border-border-subtle shrink-0">
        <div>
          <h1 className="text-lg font-semibold text-text-primary tracking-tight flex items-center gap-2">
            <Brain className="w-5 h-5 text-accent" />
            Agent Long-Term Memory
          </h1>
          <p className="text-xs text-text-muted mt-0.5">
            Learned user preferences, saved workflow parameters, and persistent context facts.
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
            placeholder="Search memory keys or stored facts..."
            className="w-full h-8 bg-bg-secondary border border-border-subtle rounded-md pl-8 pr-3 text-xs text-text-primary placeholder:text-text-muted focus:border-accent/60 outline-none"
          />
        </div>

        {/* Category Filter Pills */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1">
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`px-2.5 py-1 rounded text-xs font-medium capitalize whitespace-nowrap transition-colors ${
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

      {/* Memory Cards Grid */}
      <div className="flex-1 overflow-y-auto space-y-2.5">
        {filteredMemories.length === 0 ? (
          <div className="h-48 flex flex-col items-center justify-center text-text-muted text-xs">
            No memory entries found.
          </div>
        ) : (
          filteredMemories.map((item) => (
            <div
              key={item.id}
              className="p-3.5 rounded-lg bg-bg-secondary border border-border-subtle hover:border-border-hover transition-colors space-y-2"
            >
              <div className="flex items-center justify-between">
                <span className="font-mono text-xs font-semibold text-accent">
                  {item.key}
                </span>
                <span className="text-[10px] uppercase tracking-wider px-1.5 py-0.5 rounded bg-bg-elevated border border-border-subtle text-text-muted">
                  {item.category}
                </span>
              </div>

              <p className="text-xs text-text-primary leading-relaxed bg-bg-main p-2 rounded border border-border-subtle/40">
                {item.value}
              </p>

              <div className="flex items-center justify-between text-[10px] text-text-muted pt-1">
                <span>Updated: {item.updatedAt}</span>
                <span className="text-text-secondary cursor-pointer hover:text-accent transition-colors">
                  Copy Key
                </span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
