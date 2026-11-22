import React from "react";
import { Wrench, CheckCircle, AlertTriangle, Clock } from "lucide-react";
import { ToolActivity } from "../../types/agent";

interface ToolActivityBadgeProps {
  activity: ToolActivity;
  onApprove?: (id: string) => void;
  onReject?: (id: string) => void;
}

export const ToolActivityBadge: React.FC<ToolActivityBadgeProps> = ({
  activity,
  onApprove,
  onReject,
}) => {
  const isStaged = activity.status === "staged" || activity.requiresConfirmation;

  return (
    <div className="my-2 p-2.5 rounded-md bg-bg-elevated border border-border-subtle max-w-xl text-xs space-y-2">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 font-mono text-accent">
          <Wrench className="w-3.5 h-3.5 text-accent" />
          <span className="font-semibold">{activity.toolName}</span>
        </div>
        <div className="flex items-center gap-1.5 text-[11px]">
          {activity.status === "completed" && (
            <span className="flex items-center gap-1 text-status-success font-medium">
              <CheckCircle className="w-3 h-3" />
              Completed {activity.durationMs ? `(${activity.durationMs.toFixed(1)}ms)` : ""}
            </span>
          )}
          {isStaged && (
            <span className="flex items-center gap-1 text-status-warning font-medium">
              <AlertTriangle className="w-3 h-3" />
              Confirmation Required
            </span>
          )}
          {activity.status === "running" && (
            <span className="flex items-center gap-1 text-text-muted">
              <Clock className="w-3 h-3 animate-spin text-accent" />
              Executing...
            </span>
          )}
        </div>
      </div>

      {/* Arguments preview */}
      {activity.arguments && Object.keys(activity.arguments).length > 0 && (
        <div className="bg-bg-main p-1.5 rounded font-mono text-[11px] text-text-secondary overflow-x-auto border border-border-subtle/50">
          {JSON.stringify(activity.arguments, null, 2)}
        </div>
      )}

      {/* Result or Staged description */}
      {activity.resultSummary && (
        <div className="text-text-secondary text-[11px]">
          {activity.resultSummary}
        </div>
      )}

      {/* Confirmation Actions */}
      {isStaged && (
        <div className="pt-1 flex items-center gap-2">
          <button
            onClick={() => onApprove?.(activity.id)}
            className="px-2.5 py-1 rounded bg-accent hover:bg-accent-hover text-bg-main font-semibold text-xs transition-colors"
          >
            Approve & Execute
          </button>
          <button
            onClick={() => onReject?.(activity.id)}
            className="px-2.5 py-1 rounded bg-bg-hover hover:bg-border-subtle text-text-secondary text-xs transition-colors"
          >
            Reject
          </button>
        </div>
      )}
    </div>
  );
};
