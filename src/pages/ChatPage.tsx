import React, { useState, useRef, useEffect } from "react";
import {
  ArrowUp,
  Paperclip,
  ChevronDown,
  ChevronRight,
  Bot,
  User,
  Square,
  Sparkles
} from "lucide-react";
import { ChatMessage, NavPage } from "../types/agent";
import { mockInitialMessages } from "../lib/mockData";
import { EmptyChatState } from "../components/chat/EmptyChatState";
import { ToolActivityBadge } from "../components/chat/ToolActivityBadge";

interface ChatPageProps {
  onNavigate: (page: NavPage) => void;
}

export const ChatPage: React.FC<ChatPageProps> = ({ onNavigate }) => {
  const [messages, setMessages] = useState<ChatMessage[]>(mockInitialMessages);
  const [inputText, setInputText] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [expandedThinking, setExpandedThinking] = useState<Record<string, boolean>>({});
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = () => {
    if (!inputText.trim() || isGenerating) return;

    const userMessage: ChatMessage = {
      id: `msg-${Date.now()}`,
      role: "user",
      content: inputText.trim(),
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputText("");
    setIsGenerating(true);

    // Simulate Agent Thinking & Tool-Calling Response
    setTimeout(() => {
      const assistantMessage: ChatMessage = {
        id: `msg-${Date.now() + 1}`,
        role: "assistant",
        content: `I've analyzed your instruction: "${userMessage.content}".\n\nI can execute this using the local **Personal Agent Tool Engine** through Windows UI Automation or desktop actions. You can monitor progress on the **Computer** view or review past steps in **Activity**.`,
        thinkingContent: `Interpreting intent for "${userMessage.content}". Mapping to available safe tools in ToolRegistry (44 tools active). Checking permission policies.`,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        toolActivities: [
          {
            id: `tool-${Date.now()}`,
            toolName: "get_screen_metrics",
            arguments: {},
            status: "completed",
            durationMs: 1.2,
            resultSummary: "Resolution: 1920x1080 | DPI: 1.0x | Primary Workspace Active"
          }
        ]
      };
      setMessages((prev) => [...prev, assistantMessage]);
      setIsGenerating(false);
    }, 1200);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const toggleThinking = (id: string) => {
    setExpandedThinking((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  return (
    <div className="flex-1 flex flex-col h-full overflow-hidden relative">
      {/* Scrollable Message Area */}
      <div className="flex-1 overflow-y-auto px-4 py-6">
        {messages.length === 0 ? (
          <EmptyChatState onSelectSuggestion={(prompt) => setInputText(prompt)} />
        ) : (
          <div className="max-w-3xl mx-auto space-y-6">
            {messages.map((msg) => {
              const isUser = msg.role === "user";
              return (
                <div key={msg.id} className={`flex gap-3 text-xs leading-relaxed ${isUser ? "justify-end" : "justify-start"}`}>
                  {!isUser && (
                    <div className="w-7 h-7 rounded-md bg-accent/15 border border-accent/25 flex items-center justify-center text-accent shrink-0 mt-0.5">
                      <Bot className="w-4 h-4" />
                    </div>
                  )}

                  <div className={`max-w-[85%] space-y-2 ${isUser ? "items-end" : "items-start"}`}>
                    {/* Collapsible Thinking Block */}
                    {msg.thinkingContent && (
                      <div className="border border-border-subtle rounded bg-bg-secondary p-2 max-w-xl text-[11px]">
                        <button
                          onClick={() => toggleThinking(msg.id)}
                          className="flex items-center gap-1.5 text-text-muted hover:text-text-secondary font-medium w-full text-left"
                        >
                          {expandedThinking[msg.id] ? (
                            <ChevronDown className="w-3 h-3 text-accent" />
                          ) : (
                            <ChevronRight className="w-3 h-3 text-accent" />
                          )}
                          <span>Reasoning Process</span>
                        </button>
                        {expandedThinking[msg.id] && (
                          <div className="mt-2 text-text-muted font-mono text-[10px] pl-4 border-l border-border-subtle whitespace-pre-wrap">
                            {msg.thinkingContent}
                          </div>
                        )}
                      </div>
                    )}

                    {/* Message Bubble */}
                    <div
                      className={`p-3.5 rounded-lg whitespace-pre-wrap ${
                        isUser
                          ? "bg-bg-elevated border border-border-subtle text-text-primary"
                          : "bg-bg-secondary border border-border-subtle text-text-primary shadow-sm"
                      }`}
                    >
                      {msg.content}
                    </div>

                    {/* Embedded Tool Activities */}
                    {msg.toolActivities && msg.toolActivities.length > 0 && (
                      <div className="space-y-1">
                        {msg.toolActivities.map((act) => (
                          <ToolActivityBadge key={act.id} activity={act} />
                        ))}
                      </div>
                    )}

                    {/* Timestamp */}
                    <div className={`text-[10px] text-text-muted px-1 ${isUser ? "text-right" : "text-left"}`}>
                      {msg.timestamp}
                    </div>
                  </div>

                  {isUser && (
                    <div className="w-7 h-7 rounded-md bg-bg-hover border border-border-subtle flex items-center justify-center text-text-secondary shrink-0 mt-0.5">
                      <User className="w-4 h-4" />
                    </div>
                  )}
                </div>
              );
            })}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Floating Centered Chat Composer */}
      <div className="p-4 bg-gradient-to-t from-bg-main via-bg-main to-transparent shrink-0">
        <div className="max-w-3xl mx-auto">
          <div className="relative rounded-xl bg-bg-secondary border border-border-subtle focus-within:border-accent/60 shadow-lg transition-colors p-2.5">
            <textarea
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyDown={handleKeyDown}
              rows={2}
              placeholder="Ask anything or command computer control... (Enter to send, Shift+Enter for new line)"
              className="w-full bg-transparent resize-none outline-none text-xs text-text-primary placeholder:text-text-muted px-1 py-0.5 leading-relaxed"
            />

            <div className="flex items-center justify-between pt-1 border-t border-border-subtle/50 mt-1">
              {/* Left actions / attachments */}
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  title="Attach file (coming in Milestone D)"
                  className="p-1.5 rounded hover:bg-bg-elevated text-text-muted hover:text-text-secondary transition-colors"
                >
                  <Paperclip className="w-3.5 h-3.5" />
                </button>
                <div className="px-2 py-0.5 rounded bg-bg-elevated text-[10px] text-text-muted border border-border-subtle">
                  qwen3:8b (Local Ollama)
                </div>
              </div>

              {/* Right Send / Stop button */}
              <div className="flex items-center gap-1.5">
                {isGenerating ? (
                  <button
                    onClick={() => setIsGenerating(false)}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-status-error/20 hover:bg-status-error/30 text-status-error text-xs font-medium transition-colors"
                  >
                    <Square className="w-3 h-3 fill-status-error" />
                    <span>Stop</span>
                  </button>
                ) : (
                  <button
                    onClick={handleSend}
                    disabled={!inputText.trim()}
                    className={`p-1.5 rounded-md flex items-center justify-center transition-all ${
                      inputText.trim()
                        ? "bg-accent hover:bg-accent-hover text-bg-main shadow"
                        : "bg-bg-elevated text-text-muted cursor-not-allowed"
                    }`}
                  >
                    <ArrowUp className="w-4 h-4 stroke-[2.5]" />
                  </button>
                )}
              </div>
            </div>
          </div>
          <div className="text-[10px] text-center text-text-muted mt-1.5">
            Personal Agent operates with strict human-in-the-loop safety boundaries. Mutating actions require confirmation.
          </div>
        </div>
      </div>
    </div>
  );
};
