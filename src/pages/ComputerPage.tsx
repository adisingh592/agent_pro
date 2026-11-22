import React, { useState } from "react";
import {
  Monitor,
  Cpu,
  Layers,
  Shield,
  Activity,
  Maximize2,
  AlertOctagon,
  CheckCircle2,
  Compass
} from "lucide-react";
import { mockComputerState } from "../lib/mockData";

export const ComputerPage: React.FC = () => {
  const [emergencyActive, setEmergencyActive] = useState(
    mockComputerState.automationStatus.emergencyStopActive
  );

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between pb-4 border-b border-border-subtle">
        <div>
          <h1 className="text-lg font-semibold text-text-primary tracking-tight flex items-center gap-2">
            <Monitor className="w-5 h-5 text-accent" />
            Computer Control & Telemetry
          </h1>
          <p className="text-xs text-text-muted mt-0.5">
            Real-time desktop telemetry, active window inspection, and automation grounding engine.
          </p>
        </div>

        {/* Emergency Stop Button */}
        <button
          onClick={() => setEmergencyActive(!emergencyActive)}
          className={`flex items-center gap-2 px-3 py-1.5 rounded-md text-xs font-semibold transition-all ${
            emergencyActive
              ? "bg-status-error text-white shadow-lg animate-pulse"
              : "bg-bg-elevated hover:bg-bg-hover text-status-warning border border-border-subtle"
          }`}
        >
          <AlertOctagon className="w-4 h-4" />
          <span>{emergencyActive ? "EMERGENCY STOPPED" : "Trigger Emergency Stop"}</span>
        </button>
      </div>

      {/* Main Grid: Telemetry & Active Window */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Hardware Status */}
        <div className="p-4 rounded-lg bg-bg-secondary border border-border-subtle space-y-3">
          <div className="flex items-center justify-between text-xs font-medium text-text-secondary">
            <span className="flex items-center gap-1.5">
              <Cpu className="w-3.5 h-3.5 text-accent" />
              Processor & Memory
            </span>
            <span className="text-status-success font-mono">Normal</span>
          </div>

          <div className="space-y-2 text-xs">
            <div>
              <div className="flex justify-between text-[11px] text-text-muted mb-1">
                <span>CPU Usage</span>
                <span className="text-text-primary font-mono">{mockComputerState.cpuUsagePercent}%</span>
              </div>
              <div className="h-1.5 w-full bg-bg-elevated rounded-full overflow-hidden">
                <div
                  className="h-full bg-accent rounded-full transition-all"
                  style={{ width: `${mockComputerState.cpuUsagePercent}%` }}
                />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-[11px] text-text-muted mb-1">
                <span>System RAM ({mockComputerState.ramUsedGb} GB / {mockComputerState.ramTotalGb} GB)</span>
                <span className="text-text-primary font-mono">
                  {((mockComputerState.ramUsedGb / mockComputerState.ramTotalGb) * 100).toFixed(0)}%
                </span>
              </div>
              <div className="h-1.5 w-full bg-bg-elevated rounded-full overflow-hidden">
                <div
                  className="h-full bg-accent rounded-full transition-all"
                  style={{ width: `${(mockComputerState.ramUsedGb / mockComputerState.ramTotalGb) * 100}%` }}
                />
              </div>
            </div>
          </div>
          <div className="pt-2 border-t border-border-subtle/50 text-[11px] text-text-muted">
            {mockComputerState.cpuModel}
          </div>
        </div>

        {/* GPU & VRAM Status */}
        <div className="p-4 rounded-lg bg-bg-secondary border border-border-subtle space-y-3">
          <div className="flex items-center justify-between text-xs font-medium text-text-secondary">
            <span className="flex items-center gap-1.5">
              <Activity className="w-3.5 h-3.5 text-accent" />
              Hardware GPU (CUDA)
            </span>
            <span className="text-accent font-mono text-[11px]">70% Offload</span>
          </div>

          <div className="space-y-2 text-xs">
            <div>
              <div className="flex justify-between text-[11px] text-text-muted mb-1">
                <span>VRAM Allocation ({mockComputerState.vramUsedMb} MiB / {mockComputerState.vramTotalMb} MiB)</span>
                <span className="text-text-primary font-mono">
                  {((mockComputerState.vramUsedMb / mockComputerState.vramTotalMb) * 100).toFixed(0)}%
                </span>
              </div>
              <div className="h-1.5 w-full bg-bg-elevated rounded-full overflow-hidden">
                <div
                  className="h-full bg-accent rounded-full transition-all"
                  style={{ width: `${(mockComputerState.vramUsedMb / mockComputerState.vramTotalMb) * 100}%` }}
                />
              </div>
            </div>
          </div>
          <div className="pt-2 border-t border-border-subtle/50 text-[11px] text-text-muted">
            {mockComputerState.gpuName}
          </div>
        </div>

        {/* Display & Grounding Info */}
        <div className="p-4 rounded-lg bg-bg-secondary border border-border-subtle space-y-3">
          <div className="flex items-center justify-between text-xs font-medium text-text-secondary">
            <span className="flex items-center gap-1.5">
              <Compass className="w-3.5 h-3.5 text-accent" />
              Coordinate Grounding
            </span>
            <span className="text-status-success font-mono text-[11px]">Calibrated</span>
          </div>

          <div className="space-y-1.5 text-[11px]">
            <div className="flex justify-between py-0.5 border-b border-border-subtle/40">
              <span className="text-text-muted">Display Resolution:</span>
              <span className="text-text-primary font-mono">{mockComputerState.display.resolution}</span>
            </div>
            <div className="flex justify-between py-0.5 border-b border-border-subtle/40">
              <span className="text-text-muted">Scale Factor:</span>
              <span className="text-text-primary font-mono">{mockComputerState.display.dpiScale.toFixed(2)}x (96 DPI)</span>
            </div>
            <div className="flex justify-between py-0.5">
              <span className="text-text-muted">Coordinate Scale:</span>
              <span className="text-accent font-mono">[0, 1000] Normalized</span>
            </div>
          </div>
        </div>
      </div>

      {/* Foreground Target Window Card */}
      <div className="p-4 rounded-lg bg-bg-secondary border border-border-subtle space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-xs font-semibold uppercase tracking-wider text-text-secondary flex items-center gap-2">
            <Maximize2 className="w-3.5 h-3.5 text-accent" />
            Active Foreground Window (Scope Target)
          </h2>
          <span className="text-[11px] px-2 py-0.5 rounded bg-bg-elevated text-text-muted border border-border-subtle">
            Tracking via win32gui
          </span>
        </div>

        {mockComputerState.activeWindow ? (
          <div className="grid grid-cols-1 sm:grid-cols-4 gap-3 bg-bg-main p-3 rounded border border-border-subtle text-xs">
            <div>
              <span className="text-[11px] text-text-muted block">Window Title</span>
              <span className="text-text-primary font-medium truncate block">
                {mockComputerState.activeWindow.title}
              </span>
            </div>
            <div>
              <span className="text-[11px] text-text-muted block">Process Executable</span>
              <span className="text-accent font-mono truncate block">
                {mockComputerState.activeWindow.processName}
              </span>
            </div>
            <div>
              <span className="text-[11px] text-text-muted block">Process ID (PID)</span>
              <span className="text-text-secondary font-mono block">
                {mockComputerState.activeWindow.pid}
              </span>
            </div>
            <div>
              <span className="text-[11px] text-text-muted block">Handle (HWND)</span>
              <span className="text-text-secondary font-mono block">
                0x{mockComputerState.activeWindow.hwnd.toString(16).toUpperCase()}
              </span>
            </div>
          </div>
        ) : (
          <div className="text-xs text-text-muted">No foreground window currently tracked.</div>
        )}
      </div>

      {/* Subsystem Health Status */}
      <div className="p-4 rounded-lg bg-bg-secondary border border-border-subtle space-y-3">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-text-secondary flex items-center gap-2">
          <Shield className="w-3.5 h-3.5 text-accent" />
          Automation Engine Subsystems
        </h2>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <div className="p-3 rounded bg-bg-elevated border border-border-subtle flex items-center gap-3">
            <CheckCircle2 className="w-4 h-4 text-status-success shrink-0" />
            <div>
              <div className="text-xs font-medium text-text-primary">Windows UI Automation</div>
              <div className="text-[11px] text-text-muted">Tree inspector, invoke & value patterns ready</div>
            </div>
          </div>

          <div className="p-3 rounded bg-bg-elevated border border-border-subtle flex items-center gap-3">
            <CheckCircle2 className="w-4 h-4 text-status-success shrink-0" />
            <div>
              <div className="text-xs font-medium text-text-primary">Desktop Actions</div>
              <div className="text-[11px] text-text-muted">Physical mouse, keyboard & drag simulation ready</div>
            </div>
          </div>

          <div className="p-3 rounded bg-bg-elevated border border-border-subtle flex items-center gap-3">
            <CheckCircle2 className="w-4 h-4 text-status-success shrink-0" />
            <div>
              <div className="text-xs font-medium text-text-primary">Failsafe Circuit Breaker</div>
              <div className="text-[11px] text-text-muted">Corner slam (0,0) and keyup release armed</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
