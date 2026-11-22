import React, { useState } from "react";
import { ArrowLeft, Play, Terminal, FolderOpen, Save, RefreshCw, FileCode, CheckCircle2 } from "lucide-react";
import { NavPage } from "../types/agent";

interface IdePageProps {
  onNavigate: (page: NavPage) => void;
}

export const IdePage: React.FC<IdePageProps> = ({ onNavigate }) => {
  const [code, setCode] = useState<string>(
`# Personal Agent - Autonomous Code Generation
# Target: Windows 11 Desktop Agent Script
import sys
from app.agent.tools.registry import get_tool_registry

def run_agent_workflow():
    registry = get_tool_registry()
    tools = registry.list_tools()
    print(f"Loaded {len(tools)} local tools.")
    return tools

if __name__ == "__main__":
    run_agent_workflow()`
  );

  const [output, setOutput] = useState<string>("Personal Agent IDE Workspace ready. Press 'Run with Agent' to execute.");
  const [isRunning, setIsRunning] = useState(false);

  const handleRun = () => {
    setIsRunning(true);
    setOutput("Executing script through Personal Agent sandbox...\nChecking safety permissions...");
    setTimeout(() => {
      setOutput(
`[Personal Agent Engine - Execution Log]
> python -u workspace_script.py
Loaded 44 local tools.
ToolRegistry: Ready
UI Automation: Active
Safety Guard: Armed
Execution finished successfully in 42.1ms (Exit code 0)`
      );
      setIsRunning(false);
    }, 800);
  };

  return (
    <div className="h-full flex flex-col bg-[#050907] text-[#F1F5ED] select-none">
      {/* Top IDE Header */}
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
            <FileCode className="w-4 h-4 text-[#9BE34A]" />
            <span>workspace_script.py</span>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleRun}
            disabled={isRunning}
            className="flex items-center gap-1.5 px-3 py-1 rounded-lg bg-[#9BE34A] hover:bg-[#C5FF67] text-[#050907] font-semibold text-xs shadow-[0_0_12px_rgba(155,227,74,0.35)] transition-all"
          >
            {isRunning ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Play className="w-3.5 h-3.5 fill-current" />}
            <span>Run with Agent</span>
          </button>
        </div>
      </header>

      {/* Editor Body */}
      <div className="flex-1 flex overflow-hidden">
        {/* Code Area */}
        <div className="flex-1 flex flex-col border-r border-[rgba(156,190,153,0.15)]">
          <div className="bg-[#09150D] px-4 py-1.5 text-[11px] text-[#A4ADA2] border-b border-[rgba(156,190,153,0.1)] flex items-center justify-between">
            <span>Python 3.12 • UTF-8</span>
            <span className="flex items-center gap-1 text-[#9BE34A]">
              <CheckCircle2 className="w-3 h-3" /> Agent Copilot Active
            </span>
          </div>
          <textarea
            value={code}
            onChange={(e) => setCode(e.target.value)}
            className="flex-1 p-4 bg-[#050907] font-mono text-xs text-[#F1F5ED] resize-none outline-none focus:outline-none border-none leading-relaxed"
            spellCheck={false}
          />
        </div>

        {/* Terminal Output */}
        <div className="w-80 md:w-96 flex flex-col bg-[#071009]">
          <div className="bg-[#09150D] px-4 py-1.5 text-[11px] text-[#A4ADA2] border-b border-[rgba(156,190,153,0.1)] flex items-center gap-2 font-mono">
            <Terminal className="w-3.5 h-3.5 text-[#9BE34A]" />
            <span>Agent Terminal Output</span>
          </div>
          <pre className="flex-1 p-4 font-mono text-[11px] text-[#9BE34A] whitespace-pre-wrap overflow-y-auto leading-relaxed">
            {output}
          </pre>
        </div>
      </div>
    </div>
  );
};
