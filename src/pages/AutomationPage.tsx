import React, { useState } from "react";
import { ArrowLeft, Zap, Play, CheckCircle2, Clock, Plus, ShieldCheck, RefreshCw } from "lucide-react";
import { NavPage } from "../types/agent";

interface AutomationPageProps {
  onNavigate: (page: NavPage) => void;
}

interface WorkflowItem {
  id: string;
  name: string;
  description: string;
  trigger: string;
  stepsCount: number;
  lastRun: string;
  status: "idle" | "running" | "scheduled";
}

export const AutomationPage: React.FC<AutomationPageProps> = ({ onNavigate }) => {
  const [workflows, setWorkflows] = useState<WorkflowItem[]>([
    {
      id: "wf-1",
      name: "Desktop Health & App Sync",
      description: "Inspect open windows, log memory state, and alert if high RAM detected.",
      trigger: "Every morning at 09:00 AM",
      stepsCount: 4,
      lastRun: "Today, 09:00 AM (Success)",
      status: "scheduled",
    },
    {
      id: "wf-2",
      name: "Smart Code Workspace Setup",
      description: "Launch VS Code, open project directory, and initialize local Ollama model.",
      trigger: "Manual / Voice Command",
      stepsCount: 3,
      lastRun: "Yesterday, 19:40 PM",
      status: "idle",
    },
    {
      id: "wf-3",
      name: "Auto-Archive Old Screenshots",
      description: "Scan desktop folder, move png files older than 7 days to archive folder.",
      trigger: "Weekly on Sundays",
      stepsCount: 5,
      lastRun: "3 days ago",
      status: "idle",
    },
  ]);

  const [runningId, setRunningId] = useState<string | null>(null);

  const handleRunWorkflow = (id: string) => {
    setRunningId(id);
    setTimeout(() => {
      setRunningId(null);
    }, 1500);
  };

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
            <Zap className="w-4 h-4 text-[#9BE34A]" />
            <span>Automations & Workflows</span>
          </div>
        </div>

        <button
          onClick={() => {}}
          className="flex items-center gap-1.5 px-3 py-1 rounded-lg bg-[#9BE34A] hover:bg-[#C5FF67] text-[#050907] font-semibold text-xs transition-all shadow-[0_0_12px_rgba(155,227,74,0.35)]"
        >
          <Plus className="w-3.5 h-3.5" />
          <span>New Workflow</span>
        </button>
      </header>

      {/* Main Content */}
      <div className="flex-1 overflow-y-auto p-6 max-w-5xl mx-auto w-full space-y-6">
        <div>
          <h2 className="text-lg font-bold text-[#F1F5ED]">Autonomous Desktop Workflows</h2>
          <p className="text-xs text-[#A4ADA2] mt-0.5">
            Create, schedule and orchestrate automated tasks executing through Personal Agent's safe UI Automation engine.
          </p>
        </div>

        {/* Workflow Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {workflows.map((wf) => {
            const isExecuting = runningId === wf.id;
            return (
              <div
                key={wf.id}
                className="p-4 rounded-xl bg-[#09150D]/80 border border-[rgba(156,190,153,0.18)] hover:border-[rgba(155,227,74,0.4)] shadow-[0_4px_20px_rgba(0,0,0,0.5)] transition-all flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="w-8 h-8 rounded-lg bg-[#0E2214] border border-[rgba(155,227,74,0.25)] flex items-center justify-center text-[#9BE34A]">
                      <Zap className="w-4 h-4" />
                    </span>
                    <span className="text-[10px] px-2 py-0.5 rounded-full bg-[#112417] text-[#9BE34A] border border-[rgba(155,227,74,0.25)]">
                      {wf.stepsCount} steps
                    </span>
                  </div>

                  <h3 className="text-sm font-semibold text-[#F1F5ED]">{wf.name}</h3>
                  <p className="text-xs text-[#A4ADA2] mt-1 line-clamp-2 leading-relaxed">
                    {wf.description}
                  </p>
                </div>

                <div className="mt-4 pt-3 border-t border-[rgba(156,190,153,0.12)]">
                  <div className="flex items-center gap-1.5 text-[11px] text-[#6F796F] mb-3">
                    <Clock className="w-3 h-3" />
                    <span>{wf.trigger}</span>
                  </div>

                  <div className="flex items-center justify-between">
                    <span className="text-[10px] text-[#A4ADA2] flex items-center gap-1">
                      <ShieldCheck className="w-3 h-3 text-[#9BE34A]" /> Safe Mode Armed
                    </span>
                    <button
                      onClick={() => handleRunWorkflow(wf.id)}
                      disabled={isExecuting}
                      className="flex items-center gap-1 px-2.5 py-1 rounded-md bg-[#0E2014] hover:bg-[#163320] border border-[rgba(155,227,74,0.3)] text-xs font-medium text-[#9BE34A] hover:text-[#C5FF67] transition-all"
                    >
                      {isExecuting ? (
                        <>
                          <RefreshCw className="w-3 h-3 animate-spin" />
                          <span>Running...</span>
                        </>
                      ) : (
                        <>
                          <Play className="w-3 h-3 fill-current" />
                          <span>Run Now</span>
                        </>
                      )}
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
