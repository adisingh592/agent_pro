import React, { useState } from "react";
import {
  CheckSquare,
  Clock,
  CheckCircle,
  AlertCircle,
  Plus,
  Filter
} from "lucide-react";
import { mockTasks } from "../lib/mockData";
import { AgentTask } from "../types/agent";

export const TasksPage: React.FC = () => {
  const [tasks, setTasks] = useState<AgentTask[]>(mockTasks);
  const [filterStatus, setFilterStatus] = useState<string>("all");
  const [newTitle, setNewTitle] = useState("");

  const filteredTasks = tasks.filter((t) => {
    if (filterStatus === "all") return true;
    return t.status === filterStatus;
  });

  const handleAddTask = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle.trim()) return;

    const newTask: AgentTask = {
      id: `task-${Date.now()}`,
      title: newTitle.trim(),
      description: "User scheduled task for Personal Agent execution.",
      status: "pending",
      priority: "medium",
      createdAt: "Just now"
    };
    setTasks([newTask, ...tasks]);
    setNewTitle("");
  };

  const getPriorityBadge = (priority: AgentTask["priority"]) => {
    switch (priority) {
      case "high":
        return <span className="px-1.5 py-0.5 rounded text-[10px] bg-status-error/15 text-status-error font-medium">High</span>;
      case "medium":
        return <span className="px-1.5 py-0.5 rounded text-[10px] bg-accent/15 text-accent font-medium">Medium</span>;
      default:
        return <span className="px-1.5 py-0.5 rounded text-[10px] bg-bg-elevated text-text-muted font-medium">Low</span>;
    }
  };

  return (
    <div className="flex-1 flex flex-col h-full overflow-hidden p-6 space-y-5">
      {/* Page Header */}
      <div className="flex items-center justify-between pb-4 border-b border-border-subtle shrink-0">
        <div>
          <h1 className="text-lg font-semibold text-text-primary tracking-tight flex items-center gap-2">
            <CheckSquare className="w-5 h-5 text-accent" />
            Agent Tasks & Workflows
          </h1>
          <p className="text-xs text-text-muted mt-0.5">
            Manage scheduled, autonomous, and completed task queues.
          </p>
        </div>
      </div>

      {/* Add Task Input Form */}
      <form onSubmit={handleAddTask} className="flex gap-2 shrink-0">
        <input
          type="text"
          value={newTitle}
          onChange={(e) => setNewTitle(e.target.value)}
          placeholder="Add a new task or workflow instruction..."
          className="flex-1 h-8 bg-bg-secondary border border-border-subtle rounded-md px-3 text-xs text-text-primary placeholder:text-text-muted focus:border-accent/60 outline-none"
        />
        <button
          type="submit"
          className="flex items-center gap-1.5 px-3 py-1 bg-accent hover:bg-accent-hover text-bg-main rounded-md text-xs font-semibold transition-colors shrink-0"
        >
          <Plus className="w-3.5 h-3.5 stroke-[2.5]" />
          <span>Add Task</span>
        </button>
      </form>

      {/* Status Filters */}
      <div className="flex items-center gap-2 shrink-0 text-xs">
        {["all", "pending", "running", "completed"].map((st) => (
          <button
            key={st}
            onClick={() => setFilterStatus(st)}
            className={`px-2.5 py-1 rounded capitalize font-medium transition-colors ${
              filterStatus === st
                ? "bg-accent/15 text-accent border border-accent/25"
                : "text-text-secondary hover:text-text-primary hover:bg-bg-hover border border-border-subtle"
            }`}
          >
            {st}
          </button>
        ))}
      </div>

      {/* Task List */}
      <div className="flex-1 overflow-y-auto space-y-2.5">
        {filteredTasks.length === 0 ? (
          <div className="h-48 flex flex-col items-center justify-center text-text-muted text-xs">
            No tasks found matching current filter.
          </div>
        ) : (
          filteredTasks.map((task) => (
            <div
              key={task.id}
              className="p-3.5 rounded-lg bg-bg-secondary border border-border-subtle hover:border-border-hover transition-colors flex items-start justify-between gap-4"
            >
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-semibold text-text-primary">
                    {task.title}
                  </span>
                  {getPriorityBadge(task.priority)}
                </div>
                <p className="text-[11px] text-text-muted">
                  {task.description}
                </p>
                <div className="text-[10px] text-text-muted pt-1">
                  Created: {task.createdAt}
                  {task.completedAt && ` • Completed: ${task.completedAt}`}
                  {task.stepCount && ` • ${task.stepCount} steps executed`}
                </div>
              </div>

              <div className="shrink-0 flex items-center gap-1.5 text-xs font-medium">
                {task.status === "completed" && (
                  <span className="flex items-center gap-1 text-status-success text-[11px]">
                    <CheckCircle className="w-3.5 h-3.5" />
                    Done
                  </span>
                )}
                {task.status === "pending" && (
                  <span className="flex items-center gap-1 text-text-muted text-[11px]">
                    <Clock className="w-3.5 h-3.5" />
                    Pending
                  </span>
                )}
                {task.status === "running" && (
                  <span className="flex items-center gap-1 text-accent text-[11px]">
                    <Clock className="w-3.5 h-3.5 animate-spin" />
                    Running
                  </span>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
