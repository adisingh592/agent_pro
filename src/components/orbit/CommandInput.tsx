import React, { useState } from "react";
import { Paperclip, Mic, ArrowRight } from "lucide-react";

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
    <div className={`relative w-[760px] max-w-[92vw] z-30 select-none ${className}`}>
      {/* Intense Glowing Backlight Underneath */}
      <div
        className={`absolute -bottom-2.5 left-1/2 -translate-x-1/2 w-[460px] h-4 rounded-full blur-[20px] transition-all duration-300 pointer-events-none ${
          isFocused ? "opacity-100 scale-105" : "opacity-85"
        }`}
        style={{
          background: "radial-gradient(ellipse at center, #9BE34A 0%, rgba(155, 227, 74, 0.7) 45%, transparent 80%)",
        }}
      />

      {/* Main Pill Floating Form matching reference */}
      <form
        onSubmit={handleSubmit}
        className={`relative flex items-center h-14 md:h-[58px] px-5 rounded-full transition-all duration-300
          bg-[#07140B]/90 backdrop-blur-2xl border
          ${isFocused 
            ? "border-[#9BE34A] shadow-[0_0_28px_rgba(155,227,74,0.4)]" 
            : "border-[rgba(155,227,74,0.45)] hover:border-[#9BE34A] shadow-[0_12px_40px_rgba(0,0,0,0.6)]"
          }`}
      >
        {/* Left Four-pointed Star Sparkle Icon matching reference */}
        <div className="flex items-center pl-0.5 pr-3 text-[#E2FF85] shrink-0">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2L14.4 9.6L22 12L14.4 14.4L12 22L9.6 14.4L2 12L9.6 9.6L12 2Z" />
          </svg>
        </div>

        {/* Vertical thin separator */}
        <div className="w-[1px] h-5 bg-[rgba(156,190,153,0.3)] mr-3 shrink-0" />

        {/* Text Input */}
        <input
          type="text"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          placeholder={placeholder}
          className="flex-1 bg-transparent text-sm md:text-[15px] text-white placeholder:text-[#7A8B7A] outline-none border-none focus:ring-0 focus:outline-none"
        />

        {/* Action Buttons Right */}
        <div className="flex items-center gap-2 pl-3 shrink-0">
          {/* Attachment Paperclip */}
          <button
            type="button"
            title="Attach file or context"
            className="w-8 h-8 rounded-full flex items-center justify-center text-[#B4C2B3] hover:text-white hover:bg-[rgba(156,190,153,0.15)] transition-colors cursor-pointer"
          >
            <Paperclip className="w-4 h-4" />
          </button>

          {/* Voice Microphone */}
          <button
            type="button"
            title="Voice input"
            className="w-8 h-8 rounded-full flex items-center justify-center text-[#B4C2B3] hover:text-white hover:bg-[rgba(156,190,153,0.15)] transition-colors cursor-pointer"
          >
            <Mic className="w-4 h-4" />
          </button>

          {/* Send Circular Button in Vibrant Lime Accent */}
          <button
            type="submit"
            disabled={!value.trim()}
            title="Send instruction to Personal Agent"
            className={`w-[36px] h-[36px] rounded-full flex items-center justify-center transition-all duration-200
              ${value.trim()
                ? "bg-[#9BE34A] text-[#050907] hover:bg-[#C5FF67] hover:scale-105 active:scale-95 shadow-[0_0_16px_rgba(155,227,74,0.6)] cursor-pointer"
                : "bg-[#9BE34A] text-[#050907] opacity-90 cursor-pointer"
              }`}
          >
            <ArrowRight className="w-4 h-4 stroke-[2.5]" />
          </button>
        </div>
      </form>
    </div>
  );
};
