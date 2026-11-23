export type NavPage =
  | "orbit"
  | "rooms"
  | "chat"
  | "computer"
  | "applications"
  | "files"
  | "tasks"
  | "memory"
  | "activity"
  | "settings"
  | "ide"
  | "automation"
  | "skills"
  | "history";

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
  type?: string;
  title?: string;
  timestamp: string;
  toolName?: string;
  status: "success" | "warning" | "error" | "info" | "denied" | "aborted";
  riskLevel?: "low" | "medium" | "high";
  executionTimeMs?: number;
  durationMs?: number;
  description: string;
  caller?: string;
}

export interface SafetySetting {
  id: string;
  title: string;
  description: string;
  enabled: boolean;
  category: "safety" | "execution" | "privacy" | "network";
}
