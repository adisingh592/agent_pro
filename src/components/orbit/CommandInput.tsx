import React, { useState } from "react";
import { Sparkles, Paperclip, Mic, ArrowRight } from "lucide-react";

interface CommandInputProps {
  onSubmit: (prompt: string) => void;
  placeholder?: string;
  className?: string;
}

export const CommandInput: React.FC<CommandInputProps> = ({
  onSubmit,
  placeholder = "Ask anything, or tell me what to do...",
  className = "",
}) => {
  const [value, setValue] = useState("");
  const [isFocused, setIsFocused] = useState(false);

  const handleSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!value.trim()) return;
    onSubmit(value.trim());
    setValue("");
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className={`relative w-full max-w-2xl z-30 select-none ${className}`}>
      {/* Intense Glowing Backlight Underneath */}
      <div
        className={`absolute -bottom-2 left-1/2 -translate-x-1/2 w-[85%] h-10 rounded-full blur-xl transition-all duration-300 pointer-events-none ${
          isFocused ? "opacity-90 scale-105" : "opacity-60"
        }`}
        style={{
          background: "radial-gradient(ellipse at center, rgba(155, 227, 74, 0.75) 0%, rgba(100, 180, 50, 0.25) 60%, transparent 80%)",
        }}
      />

      {/* Main Pill Floating Form */}
      <form
        onSubmit={handleSubmit}
        className={`relative flex items-center h-14 md:h-15 px-4 rounded-full transition-all duration-300
          bg-[#07130A]/90 backdrop-blur-2xl border
          ${isFocused 
            ? "border-[#9BE34A] shadow-[0_0_25px_rgba(155,227,74,0.35)]" 
            : "border-[rgba(156,190,153,0.22)] hover:border-[rgba(155,227,74,0.4)] shadow-[0_10px_35px_rgba(0,0,0,0.6)]"
          }`}
      >
        {/* Left Four-pointed Star / Sparkle Icon */}
        <div className="flex items-center pl-1 pr-3 text-[#C5FF67] shrink-0">
          <Sparkles className="w-5 h-5 drop-shadow-[0_0_10px_rgba(155,227,74,0.8)]" />
        </div>

        {/* Vertical subtle divider */}
        <div className="w-[1px] h-5 bg-[rgba(156,190,153,0.2)] mr-3 shrink-0" />

        {/* Text Input */}
        <input
          type="text"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          placeholder={placeholder}
          className="flex-1 bg-transparent text-sm md:text-[15px] text-[#F1F5ED] placeholder:text-[#6F796F] outline-none border-none focus:ring-0 focus:outline-none"
        />

        {/* Action Buttons Right */}
        <div className="flex items-center gap-2 pl-2 shrink-0">
          {/* Attachment Paperclip */}
          <button
            type="button"
            title="Attach file or context"
            className="w-8 h-8 rounded-full flex items-center justify-center text-[#A4ADA2] hover:text-[#F1F5ED] hover:bg-[rgba(156,190,153,0.12)] transition-colors"
          >
            <Paperclip className="w-4 h-4" />
          </button>

          {/* Voice Microphone */}
          <button
            type="button"
            title="Voice input"
            className="w-8 h-8 rounded-full flex items-center justify-center text-[#A4ADA2] hover:text-[#F1F5ED] hover:bg-[rgba(156,190,153,0.12)] transition-colors"
          >
            <Mic className="w-4 h-4" />
          </button>

          {/* Send Circular Button in Lime Accent */}
          <button
            type="submit"
            disabled={!value.trim()}
            title="Send instruction to Personal Agent"
            className={`w-9 h-9 rounded-full flex items-center justify-center transition-all duration-200
              ${value.trim()
                ? "bg-[#9BE34A] text-[#050907] hover:bg-[#C5FF67] hover:scale-105 active:scale-95 shadow-[0_0_15px_rgba(155,227,74,0.5)] cursor-pointer"
                : "bg-[#9BE34A]/80 text-[#050907]/70 cursor-pointer"
              }`}
          >
            <ArrowRight className="w-4 h-4 stroke-[2.5]" />
          </button>
        </div>
      </form>
    </div>
  );
};
