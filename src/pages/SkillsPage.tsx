import React, { useState } from "react";
import { ArrowLeft, LayoutGrid, Search, Wrench, Shield, CheckCircle2, ChevronRight } from "lucide-react";
import { NavPage } from "../types/agent";

interface SkillsPageProps {
  onNavigate: (page: NavPage) => void;
}

interface ToolCard {
  name: string;
  category: "UI Automation" | "Desktop Action" | "System Control" | "Files" | "Processes";
  description: string;
  riskLevel: "Low" | "Medium" | "High";
  requiresApproval: boolean;
}

export const SkillsPage: React.FC<SkillsPageProps> = ({ onNavigate }) => {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCategory, setSelectedCategory] = useState<string>("All");

  const tools: ToolCard[] = [
    {
      name: "list_windows",
      category: "UI Automation",
      description: "Discovers all visible top-level desktop windows with handles, titles, and processes.",
      riskLevel: "Low",
      requiresApproval: false,
    },
    {
      name: "inspect_window_elements",
      category: "UI Automation",
      description: "Extracts full accessibility hierarchy, controls, buttons, and text fields in targeted window.",
      riskLevel: "Low",
      requiresApproval: false,
    },
    {
      name: "click_element",
      category: "UI Automation",
      description: "Invokes native accessibility click on UI controls without moving physical mouse.",
      riskLevel: "Medium",
      requiresApproval: false,
    },
    {
      name: "click_coordinate",
      category: "Desktop Action",
      description: "Sends calibrated hardware mouse click event at exact screen coordinates (X, Y).",
      riskLevel: "Medium",
      requiresApproval: false,
    },
    {
      name: "type_text",
      category: "Desktop Action",
      description: "Synthesizes keyboard input into active focused UI control or desktop location.",
      riskLevel: "Medium",
      requiresApproval: false,
    },
    {
      name: "launch_application",
      category: "System Control",
      description: "Executes verified desktop applications from predefined catalog or system paths.",
      riskLevel: "High",
      requiresApproval: true,
    },
    {
      name: "terminate_process",
      category: "Processes",
      description: "Stops targeted background process safely with user confirmation.",
      riskLevel: "High",
      requiresApproval: true,
    },
    {
      name: "read_file_safe",
      category: "Files",
      description: "Safely reads text contents from whitelisted project or workspace directory paths.",
      riskLevel: "Low",
      requiresApproval: false,
    },
    {
      name: "write_file_safe",
      category: "Files",
      description: "Creates or modifies files with automatic backup snapshots and rollback protection.",
      riskLevel: "Medium",
      requiresApproval: false,
    },
  ];

  const filteredTools = tools.filter((tool) => {
    const matchesSearch = tool.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      tool.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCat = selectedCategory === "All" || tool.category === selectedCategory;
    return matchesSearch && matchesCat;
  });

  return (
    <div className="h-full flex flex-col bg-[#050907] text-[#F1F5ED] select-none">
      {/* Top Header */}
      <header className="h-12 border-b border-[rgba(156,190,153,0.15)] bg-[#07130A] px-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <button
            onClick={() => onNavigate("orbit")}
            className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-[#0E2014] hover:bg-[#163320] border border-[rgba(155,227,74,0.3)] text-xs text-[#9BE34A] transition-colors"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Orbit Home</span>
          </button>
          <div className="w-[1px] h-4 bg-[rgba(156,190,153,0.2)]" />
          <div className="flex items-center gap-2 text-xs font-semibold">
            <LayoutGrid className="w-4 h-4 text-[#9BE34A]" />
            <span>Agent Skills & Tool Registry (44 Registered Tools)</span>
          </div>
        </div>

        <div className="relative w-64">
          <Search className="w-3.5 h-3.5 text-[#6F796F] absolute left-2.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search skills & tools..."
            className="w-full h-7 pl-8 pr-3 bg-[#0A160E] border border-[rgba(156,190,153,0.2)] rounded-lg text-xs text-[#F1F5ED] placeholder:text-[#6F796F] outline-none focus:border-[#9BE34A]"
          />
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 overflow-y-auto p-6 max-w-5xl mx-auto w-full space-y-6">
        <div>
          <h2 className="text-lg font-bold text-[#F1F5ED]">Personal Agent Capability Catalog</h2>
          <p className="text-xs text-[#A4ADA2] mt-0.5">
            Every skill is backed by strict parameter validation, permission checks, and safe local execution.
          </p>
        </div>

        {/* Tools List */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
          {filteredTools.map((tool) => (
            <div
              key={tool.name}
              className="p-4 rounded-xl bg-[#09150D]/80 border border-[rgba(156,190,153,0.18)] hover:border-[rgba(155,227,74,0.4)] transition-all flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <span className="font-mono text-xs font-semibold text-[#9BE34A]">
                    {tool.name}()
                  </span>
                  <span className="text-[10px] px-2 py-0.5 rounded-full bg-[#112417] text-[#A4ADA2] border border-[rgba(156,190,153,0.2)]">
                    {tool.category}
                  </span>
                </div>
                <p className="text-xs text-[#A4ADA2] leading-relaxed">
                  {tool.description}
                </p>
              </div>

              <div className="mt-3 pt-2.5 border-t border-[rgba(156,190,153,0.1)] flex items-center justify-between text-[11px]">
                <span className="flex items-center gap-1.5 text-[#6F796F]">
                  <Shield className="w-3 h-3 text-[#9BE34A]" />
                  Risk: <strong className="text-[#F1F5ED] font-medium">{tool.riskLevel}</strong>
                </span>
                {tool.requiresApproval ? (
                  <span className="text-[10px] text-[#D48B38] font-medium">Approval Required</span>
                ) : (
                  <span className="text-[10px] text-[#9BE34A] flex items-center gap-1">
                    <CheckCircle2 className="w-3 h-3" /> Auto-Permitted
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
