import React, { useState } from "react";
import {
  Activity,
  CheckCircle2,
  AlertTriangle,
  Info,
  Clock,
  Filter
} from "lucide-react";
import { mockActivityLogs } from "../lib/mockData";
import { ActivityEntry } from "../types/agent";

export const ActivityPage: React.FC = () => {
  const [filterType, setFilterType] = useState<string>("all");
  const [logs] = useState<ActivityEntry[]>(mockActivityLogs);

  const filteredLogs = logs.filter((log) => {
    if (filterType === "all") return true;
    return log.type === filterType;
  });

  const getStatusIcon = (status: ActivityEntry["status"]) => {
    switch (status) {
      case "success":
        return <CheckCircle2 className="w-4 h-4 text-status-success shrink-0" />;
      case "warning":
        return <AlertTriangle className="w-4 h-4 text-status-warning shrink-0" />;
      case "error":
        return <AlertTriangle className="w-4 h-4 text-status-error shrink-0" />;
      default:
        return <Info className="w-4 h-4 text-accent shrink-0" />;
    }
  };

  return (
    <div className="flex-1 flex flex-col h-full overflow-hidden p-6 space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b border-border-subtle shrink-0">
        <div>
          <h1 className="text-lg font-semibold text-text-primary tracking-tight flex items-center gap-2">
            <Activity className="w-5 h-5 text-accent" />
            Execution Activity & Audit Trail
          </h1>
          <p className="text-xs text-text-muted mt-0.5">
            Forensic timeline of agent actions, tool runs, approval decisions, and system alerts.
          </p>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex items-center gap-2 shrink-0 text-xs">
        {[
          { id: "all", label: "All Activity" },
          { id: "tool_execution", label: "Tool Runs" },
          { id: "confirmation_approved", label: "Approvals" },
          { id: "task_state", label: "Tasks" }
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setFilterType(tab.id)}
            className={`px-2.5 py-1 rounded font-medium transition-colors ${
              filterType === tab.id
                ? "bg-accent/15 text-accent border border-accent/25"
                : "text-text-secondary hover:text-text-primary hover:bg-bg-hover border border-border-subtle"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Activity Timeline List */}
      <div className="flex-1 overflow-y-auto space-y-2.5">
        {filteredLogs.map((log) => (
          <div
            key={log.id}
            className="p-3.5 rounded-lg bg-bg-secondary border border-border-subtle hover:border-border-hover transition-colors flex items-start justify-between gap-4"
          >
            <div className="flex items-start gap-3">
              <div className="mt-0.5">{getStatusIcon(log.status)}</div>
              <div className="space-y-0.5">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-semibold text-text-primary">
                    {log.title}
                  </span>
                  {log.durationMs !== undefined && (
                    <span className="text-[10px] px-1.5 py-0.2 bg-bg-elevated font-mono text-text-muted rounded border border-border-subtle">
                      {log.durationMs.toFixed(1)}ms
                    </span>
                  )}
                </div>
                <p className="text-[11px] text-text-secondary">
                  {log.description}
                </p>
              </div>
            </div>

            <div className="text-[10px] text-text-muted font-mono shrink-0">
              {log.timestamp}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
