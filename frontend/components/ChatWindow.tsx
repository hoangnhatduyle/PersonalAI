"use client";

import { useEffect, useRef } from "react";
import type { Message } from "@/lib/api";
import MessageBubble from "./Message";
import ThinkingStatus from "./ThinkingStatus";

interface Props {
  messages: Message[];
  streamingContent: string;
  isStreaming: boolean;
  thinkingStatus: string | null;
  suggestions: string[];
  newMessageIndex: number | null;
  topicColor: string;
  onSuggestionSelect: (q: string) => void;
  contactAsk: { question: string } | null;
  onSkipContact: () => void;
}

export default function ChatWindow({
  messages,
  streamingContent,
  isStreaming,
  thinkingStatus,
  suggestions,
  newMessageIndex,
  topicColor,
  onSuggestionSelect,
  contactAsk,
  onSkipContact,
}: Props) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, streamingContent, isStreaming, thinkingStatus]);

  return (
    <div className="flex-1 overflow-y-auto px-4 sm:px-6 md:px-10 lg:px-16 py-6 space-y-6 scroll-smooth">
      {messages.map((msg, i) => (
        <MessageBubble
          key={i}
          message={msg}
          highlight={i === newMessageIndex}
          topicColor={topicColor}
        />
      ))}

      {/* Thinking status — shown while waiting for first token */}
      {isStreaming && thinkingStatus && !streamingContent && (
        <ThinkingStatus status={thinkingStatus} topicColor={topicColor} />
      )}

      {/* Streaming in-progress message — shown once tokens start arriving */}
      {isStreaming && streamingContent && (
        <MessageBubble
          message={{ role: "assistant", content: streamingContent }}
          isStreaming
          topicColor={topicColor}
        />
      )}

      {/* Follow-up suggestion chips — shown after last assistant message */}
      {!isStreaming && suggestions.length > 0 && messages.at(-1)?.role === "assistant" && (
        <div className="pl-11 flex flex-col gap-2">
          <p className="text-[10px] text-zinc-600 uppercase tracking-wider font-medium">Continue the conversation</p>
          <div className="flex flex-wrap gap-2">
            {suggestions.map((s) => (
              <button
                key={s}
                onClick={() => onSuggestionSelect(s)}
                className="text-xs px-3 py-1.5 rounded-full border border-zinc-700 bg-zinc-800/60
                           text-zinc-300 hover:bg-zinc-800 hover:text-white hover:border-indigo-500/60
                           transition-all duration-150"
              >
                {s}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Contact-info ask — deterministic Skip path, deliberately distinct from suggestion chips */}
      {!isStreaming && contactAsk && messages.at(-1)?.role === "assistant" && (
        <div className="pl-11 flex flex-col gap-2 pt-1">
          <p className="text-[10px] text-zinc-600 uppercase tracking-wider font-medium">Prefer to stay anonymous?</p>
          <button
            onClick={onSkipContact}
            className="group self-start inline-flex items-center gap-2 text-xs font-medium text-zinc-400
                       border border-dashed border-zinc-600 rounded-lg px-3 py-2 bg-transparent
                       hover:border-rose-500/50 hover:text-rose-300 hover:bg-rose-500/5
                       transition-all duration-150"
          >
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-3.5 h-3.5 text-zinc-500 group-hover:text-rose-400 transition-colors">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.28 7.22a.75.75 0 00-1.06 1.06L8.94 10l-1.72 1.72a.75.75 0 101.06 1.06L10 11.06l1.72 1.72a.75.75 0 101.06-1.06L11.06 10l1.72-1.72a.75.75 0 00-1.06-1.06L10 8.94 8.28 7.22z" clipRule="evenodd" />
            </svg>
            Skip — don&apos;t share contact info
          </button>
        </div>
      )}

      <div ref={bottomRef} />
    </div>
  );
}
