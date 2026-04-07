"use client";

import { useRef, KeyboardEvent, useEffect } from "react";

interface Props {
  onSend: (message: string) => void;
  disabled?: boolean;
  isStreaming?: boolean;
  onCancel?: () => void;
  lastUserMessage?: string;
}

export default function InputBar({ onSend, disabled, isStreaming, onCancel, lastUserMessage }: Props) {
  const ref = useRef<HTMLTextAreaElement>(null);

  const handleSend = () => {
    const value = ref.current?.value.trim();
    if (!value || disabled) return;
    onSend(value);
    ref.current!.value = "";
    ref.current!.style.height = "auto";
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
      return;
    }
    // ↑ when empty — recall last user message
    if (e.key === "ArrowUp" && ref.current?.value === "" && lastUserMessage) {
      e.preventDefault();
      ref.current!.value = lastUserMessage;
      handleInput();
      // Move cursor to end
      setTimeout(() => {
        ref.current!.selectionStart = ref.current!.value.length;
        ref.current!.selectionEnd = ref.current!.value.length;
      }, 0);
    }
  };

  // Global Escape listener to cancel streaming
  useEffect(() => {
    const handler = (e: globalThis.KeyboardEvent) => {
      if (e.key === "Escape" && isStreaming) {
        onCancel?.();
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [isStreaming, onCancel]);

  const handleInput = () => {
    const el = ref.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 160)}px`;
  };

  return (
    <div className="flex-shrink-0 border-t border-zinc-800 bg-zinc-900/80 backdrop-blur-sm">
      {/* Keyboard hint bar */}
      <div className="flex items-center gap-4 px-4 sm:px-6 md:px-10 lg:px-16 pt-2 pb-0">
        <span className="text-[10px] text-zinc-600">
          <kbd className="font-mono bg-zinc-800 px-1 rounded text-zinc-500">↑</kbd>
          {" "}Recall last
        </span>
        {isStreaming ? (
          <span className="text-[10px] text-zinc-600">
            <kbd className="font-mono bg-zinc-800 px-1 rounded text-zinc-500">Esc</kbd>
            {" "}Cancel
          </span>
        ) : null}
        <span className="text-[10px] text-zinc-600 ml-auto">
          <kbd className="font-mono bg-zinc-800 px-1 rounded text-zinc-500">Shift↵</kbd>
          {" "}New line
        </span>
      </div>

      {/* Input row */}
      <div className="flex items-end gap-2 px-4 sm:px-6 md:px-10 lg:px-16 pt-2 pb-3">
        <textarea
          ref={ref}
          rows={1}
          disabled={disabled}
          placeholder="Ask me anything…"
          onKeyDown={handleKeyDown}
          onInput={handleInput}
          className="flex-1 resize-none rounded-xl bg-zinc-800 border border-zinc-700 px-4 py-2.5
                     text-sm text-zinc-100 placeholder-zinc-500 outline-none
                     focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/50
                     disabled:opacity-50 transition-colors duration-150 max-h-40 overflow-y-auto"
        />

        {/* Cancel button while streaming */}
        {isStreaming ? (
          <button
            onClick={onCancel}
            className="flex-shrink-0 w-10 h-10 rounded-xl bg-zinc-700 hover:bg-zinc-600
                       flex items-center justify-center transition-colors duration-150"
            aria-label="Cancel"
            title="Cancel (Esc)"
          >
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4 text-zinc-300">
              <path fillRule="evenodd" d="M5.47 5.47a.75.75 0 011.06 0L12 10.94l5.47-5.47a.75.75 0 111.06 1.06L13.06 12l5.47 5.47a.75.75 0 11-1.06 1.06L12 13.06l-5.47 5.47a.75.75 0 01-1.06-1.06L10.94 12 5.47 6.53a.75.75 0 010-1.06z" clipRule="evenodd" />
            </svg>
          </button>
        ) : (
          <button
            onClick={handleSend}
            disabled={disabled}
            className="flex-shrink-0 w-10 h-10 rounded-xl bg-indigo-600 hover:bg-indigo-500
                       disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center
                       transition-colors duration-150"
            aria-label="Send"
          >
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4 text-white">
              <path d="M3.478 2.405a.75.75 0 00-.926.94l2.432 7.905H13.5a.75.75 0 010 1.5H4.984l-2.432 7.905a.75.75 0 00.926.94 60.519 60.519 0 0018.445-8.986.75.75 0 000-1.218A60.517 60.517 0 003.478 2.405z" />
            </svg>
          </button>
        )}
      </div>
    </div>
  );
}
