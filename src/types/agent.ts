export type NavPage =
  | "chat"
  | "computer"
  | "applications"
  | "files"
  | "tasks"
  | "memory"
  | "activity"
  | "settings";

export interface ToolActivity {
  id: string;
  toolName: string;
  arguments: Record<string, unknown>;
  status: "staged" | "running" | "completed" | "failed";
  requiresConfirmation?: boolean;
  confirmationTitle?: string;
  riskDescription?: string;
  durationMs?: number;
  resultSummary?: string;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  timestamp: string;
  thinkingContent?: string;
  isStreaming?: boolean;
  toolActivities?: ToolActivity[];
}

export interface ComputerState {
  hostOS: string;
  windowsVersion: string;
  cpuModel: string;
  cpuUsagePercent: number;
  ramTotalGb: number;
  ramUsedGb: number;
  gpuName: string;
  vramTotalMb: number;
  vramUsedMb: number;
  activeWindow: {
    title: string;
    processName: string;
    pid: number;
    hwnd: number;
  } | null;
  display: {
    resolution: string;
    dpiScale: number;
    monitorCount: number;
  };
  automationStatus: {
    uiAutomationReady: boolean;
    coordinateGroundingReady: boolean;
    emergencyStopActive: boolean;
  };
}

export interface InstalledApp {
  id: string;
  name: string;
  category: "Development" | "Browser" | "Productivity" | "Media" | "System" | "Other";
  executablePath: string;
  isRunning: boolean;
  pid?: number;
  lastOpened?: string;
}

export interface FileItem {
  id: string;
  name: string;
  path: string;
  isDirectory: boolean;
  extension?: string;
  sizeBytes?: number;
  modifiedAt: string;
}

export interface AgentTask {
  id: string;
  title: string;
  description: string;
  status: "pending" | "running" | "completed" | "failed";
  priority: "high" | "medium" | "low";
  createdAt: string;
  completedAt?: string;
  stepCount?: number;
}

export interface MemoryItem {
  id: string;
  key: string;
  value: string;
  category: "preference" | "workflow" | "project" | "system" | "general";
  updatedAt: string;
}

export interface ActivityEntry {
  id: string;
  type: "tool_execution" | "task_state" | "confirmation_approved" | "emergency_stop" | "error";
  title: string;
  description: string;
  timestamp: string;
  status: "success" | "warning" | "error" | "info";
  durationMs?: number;
}
