"use client";

import { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import type { Message } from "@/lib/api";

interface Props {
  message: Message;
  isStreaming?: boolean;
  highlight?: boolean;
  topicColor?: string;
  isLastAssistant?: boolean;
  onRegenerate?: () => void;
  onFeedback?: (value: "up" | "down") => void;
}

export default function MessageBubble({
  message,
  isStreaming,
  highlight,
  topicColor = "bg-zinc-700",
  isLastAssistant,
  onRegenerate,
  onFeedback,
}: Props) {
  const [copied, setCopied] = useState(false);
  const [feedback, setFeedback] = useState<"up" | "down" | null>(null);
  const isUser = message.role === "user";

  const handleCopy = async () => {
    await navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  const handleFeedback = (value: "up" | "down") => {
    setFeedback(value);
    onFeedback?.(value);
  };

  return (
    <div className={`flex gap-3 ${isUser ? "flex-row-reverse" : "flex-row"} group ${highlight ? "message-highlight" : ""}`}>
      {/* Avatar */}
      <div
        className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold transition-colors duration-500
          ${isUser ? "bg-indigo-600 text-white" : `${topicColor} text-white`}`}
      >
        {isUser ? "You" : "AI"}
      </div>

      {/* Bubble */}
      <div
        className={`relative max-w-[80%] px-4 py-3 rounded-2xl text-sm leading-relaxed
          ${isUser
            ? "bg-indigo-600 text-white rounded-tr-sm"
            : "bg-zinc-800 text-zinc-100 rounded-tl-sm border border-zinc-700"
          }
        `}
      >
        {isUser ? (
          <span className="whitespace-pre-wrap">{message.content}</span>
        ) : (
          <div
            className={`prose prose-sm prose-invert max-w-none
              prose-p:my-1 prose-p:leading-relaxed
              prose-ul:my-1 prose-ul:pl-4
              prose-ol:my-1 prose-ol:pl-4
              prose-li:my-0.5
              prose-strong:text-white
              prose-code:text-indigo-300 prose-code:bg-zinc-900 prose-code:px-1 prose-code:py-0.5 prose-code:rounded prose-code:text-xs
              prose-pre:bg-zinc-900 prose-pre:border prose-pre:border-zinc-700 prose-pre:rounded-lg prose-pre:p-3 prose-pre:my-2
              prose-headings:text-white prose-headings:font-semibold
              prose-a:text-indigo-400 prose-a:no-underline hover:prose-a:underline
              ${isStreaming ? "after:inline-block after:w-0.5 after:h-4 after:bg-indigo-400 after:ml-0.5 after:animate-pulse" : ""}
            `}
          >
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {message.content}
            </ReactMarkdown>
          </div>
        )}

        {/* Source chips — assistant only, shown when retrieval was confident */}
        {!isUser && !isStreaming && message.sources && message.sources.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mt-2">
            {message.sources.map((src) => (
              <span
                key={src}
                className="text-[10px] px-2 py-0.5 rounded-full border border-zinc-600 bg-zinc-900/60 text-zinc-400"
                title={src}
              >
                {src}
              </span>
            ))}
          </div>
        )}

        {/* Action row — assistant only, appears on hover */}
        {!isUser && !isStreaming && (
          <div
            className="absolute -bottom-6 right-0 flex items-center gap-3 text-xs text-zinc-500
                       opacity-0 group-hover:opacity-100 transition-opacity duration-150"
          >
            {isLastAssistant && onRegenerate && (
              <button onClick={onRegenerate} className="hover:text-zinc-300">
                Regenerate
              </button>
            )}
            <button
              onClick={() => handleFeedback("up")}
              className={feedback === "up" ? "text-indigo-400" : "hover:text-zinc-300"}
              aria-label="Good response"
              aria-pressed={feedback === "up"}
            >
              👍
            </button>
            <button
              onClick={() => handleFeedback("down")}
              className={feedback === "down" ? "text-indigo-400" : "hover:text-zinc-300"}
              aria-label="Bad response"
              aria-pressed={feedback === "down"}
            >
              👎
            </button>
            <button onClick={handleCopy} className="hover:text-zinc-300">
              {copied ? "✓ Copied" : "Copy"}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
