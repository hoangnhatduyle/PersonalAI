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

      <div ref={bottomRef} />
    </div>
  );
}
