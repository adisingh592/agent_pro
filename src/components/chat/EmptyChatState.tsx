import React from "react";
import { FolderGit2, Monitor, Play, Sparkles } from "lucide-react";

interface EmptyChatStateProps {
  onSelectSuggestion: (prompt: string) => void;
}

export const EmptyChatState: React.FC<EmptyChatStateProps> = ({
  onSelectSuggestion,
}) => {
  const suggestions = [
    {
      title: "Organize my downloads folder",
      subtitle: "Categorize files into typed directories",
      icon: <FolderGit2 className="w-4 h-4 text-accent" />,
      prompt: "Inspect and organize my downloads folder into categorized directories."
    },
    {
      title: "Summarize what's on my desktop",
      subtitle: "Inspect active windows and visible controls",
      icon: <Monitor className="w-4 h-4 text-accent" />,
      prompt: "What windows and applications are currently active on my computer?"
    },
    {
      title: "Open an application",
      subtitle: "Search and launch verified local apps",
      icon: <Play className="w-4 h-4 text-accent" />,
      prompt: "List installed applications on this computer."
    },
    {
      title: "Help me with a task",
      subtitle: "Multi-step computer control and reasoning",
      icon: <Sparkles className="w-4 h-4 text-accent" />,
      prompt: "Help me plan and execute a desktop workflow."
    }
  ];

  return (
    <div className="h-full flex flex-col items-center justify-center p-6 text-center max-w-xl mx-auto select-none">
      <div className="w-12 h-12 rounded-2xl bg-bg-secondary border border-border-subtle flex items-center justify-center mb-5 text-accent shadow-sm">
        <Sparkles className="w-6 h-6" />
      </div>

      <h1 className="text-xl font-semibold text-text-primary tracking-tight mb-2">
        Your computer, ready when you are.
      </h1>
      <p className="text-sm text-text-secondary mb-8">
        Ask anything. Let me help you get things done.
      </p>

      {/* Suggestion Prompts */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 w-full text-left">
        {suggestions.map((item, idx) => (
          <button
            key={idx}
            onClick={() => onSelectSuggestion(item.prompt)}
            className="p-3 rounded-lg bg-bg-secondary hover:bg-bg-elevated border border-border-subtle hover:border-accent/40 transition-all text-left group"
          >
            <div className="flex items-center gap-2 mb-1">
              {item.icon}
              <span className="text-xs font-medium text-text-primary group-hover:text-accent transition-colors">
                {item.title}
              </span>
            </div>
            <p className="text-[11px] text-text-muted leading-relaxed">
              {item.subtitle}
            </p>
          </button>
        ))}
      </div>
    </div>
  );
};
