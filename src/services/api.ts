import {
  ComputerState,
  InstalledApp,
  FileItem,
  AgentTask,
  MemoryItem,
  ActivityEntry,
  ChatMessage
} from "../types/agent";
import {
  mockComputerState,
  mockInstalledApps,
  mockFiles,
  mockTasks,
  mockMemoryItems,
  mockActivityLogs,
  mockInitialMessages
} from "../lib/mockData";

/**
 * Service Abstraction Layer.
 * Defines typed API interfaces that will bridge to the Python backend
 * (via HTTP REST, WebSocket, or local IPC) in subsequent milestones.
 */
class AgentApiService {
  private isConnected = true;
  private currentModel = "qwen3:8b";
  private endpoint = "http://localhost:11434";

  async getBackendStatus(): Promise<{ connected: boolean; model: string; endpoint: string }> {
    return {
      connected: this.isConnected,
      model: this.currentModel,
      endpoint: this.endpoint
    };
  }

  async getComputerState(): Promise<ComputerState> {
    return Promise.resolve(mockComputerState);
  }

  async getInstalledApps(): Promise<InstalledApp[]> {
    return Promise.resolve(mockInstalledApps);
  }

  async getFiles(path?: string): Promise<FileItem[]> {
    return Promise.resolve(mockFiles);
  }

  async getTasks(): Promise<AgentTask[]> {
    return Promise.resolve(mockTasks);
  }

  async getMemoryItems(): Promise<MemoryItem[]> {
    return Promise.resolve(mockMemoryItems);
  }

  async getActivityLogs(): Promise<ActivityEntry[]> {
    return Promise.resolve(mockActivityLogs);
  }

  async getChatHistory(): Promise<ChatMessage[]> {
    return Promise.resolve(mockInitialMessages);
  }

  async sendChatMessage(content: string): Promise<ChatMessage> {
    const userMsg: ChatMessage = {
      id: `msg-${Date.now()}`,
      role: "user",
      content,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
    };
    return Promise.resolve(userMsg);
  }
}

export const agentApi = new AgentApiService();
