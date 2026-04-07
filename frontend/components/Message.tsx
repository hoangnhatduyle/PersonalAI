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
}

export default function MessageBubble({ message, isStreaming, highlight, topicColor = "bg-zinc-700" }: Props) {
  const [copied, setCopied] = useState(false);
  const isUser = message.role === "user";

  const handleCopy = async () => {
    await navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
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

        {/* Copy button — assistant only, appears on hover */}
        {!isUser && !isStreaming && (
          <button
            onClick={handleCopy}
            className="absolute -bottom-6 right-0 text-xs text-zinc-500 hover:text-zinc-300
                       opacity-0 group-hover:opacity-100 transition-opacity duration-150"
          >
            {copied ? "✓ Copied" : "Copy"}
          </button>
        )}
      </div>
    </div>
  );
}
