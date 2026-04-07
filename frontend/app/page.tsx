"use client";

import { useState, useCallback, useRef } from "react";
import confetti from "canvas-confetti";
import { streamChatEvents, type Message } from "@/lib/api";
import ChatWindow from "@/components/ChatWindow";
import InputBar from "@/components/InputBar";
import StarterQuestions from "@/components/StarterQuestions";
import ProfileCard from "@/components/ProfileCard";
import ProfileSheet from "@/components/ProfileSheet";

// ── Topic → Tailwind bg class (avatar + header dot) ──────
const TOPIC_COLORS: Record<string, string> = {
  general:   "bg-indigo-600",
  work:      "bg-blue-600",
  projects:  "bg-violet-600",
  education: "bg-emerald-600",
  skills:    "bg-amber-600",
  career:    "bg-rose-600",
  contact:   "bg-teal-600",
};

// ── Topic → two blob colors [top-right, bottom-left] ─────
const TOPIC_BLOB_COLORS: Record<string, [string, string]> = {
  general:   ["#6366f1", "#a855f7"],   // indigo + purple
  work:      ["#3b82f6", "#06b6d4"],   // blue + cyan
  projects:  ["#8b5cf6", "#ec4899"],   // violet + pink
  education: ["#10b981", "#3b82f6"],   // emerald + blue
  skills:    ["#f59e0b", "#ef4444"],   // amber + red
  career:    ["#f43f5e", "#f97316"],   // rose + orange
  contact:   ["#14b8a6", "#a855f7"],   // teal + purple
};

/** Convert a 6-digit hex colour to rgba(). */
function hexToRgba(hex: string, alpha: number): string {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

const CONFETTI_TRIGGERS = [
  "hire", "impressive", "amazing", "wow", "great job",
  "love it", "awesome", "brilliant",
];

export default function Home() {
  const [messages,        setMessages]        = useState<Message[]>([]);
  const [streamingContent,setStreamingContent]= useState("");
  const [isStreaming,     setIsStreaming]      = useState(false);
  const [thinkingStatus,  setThinkingStatus]  = useState<string | null>(null);
  const [topic,           setTopic]           = useState("general");
  const [suggestions,     setSuggestions]     = useState<string[]>([]);
  const [newMessageIndex, setNewMessageIndex] = useState<number | null>(null);
  const [sheetOpen,       setSheetOpen]       = useState(false);

  const abortRef = useRef<AbortController | null>(null);

  const topicColor      = TOPIC_COLORS[topic]      ?? TOPIC_COLORS.general;
  const [blobA, blobB]  = TOPIC_BLOB_COLORS[topic] ?? TOPIC_BLOB_COLORS.general;

  const lastUserMessage =
    messages.filter(m => m.role === "user").at(-1)?.content ?? "";

  const cancelStream = useCallback(() => {
    abortRef.current?.abort();
  }, []);

  const sendMessage = useCallback(async (text: string) => {
    if (isStreaming) return;

    if (CONFETTI_TRIGGERS.some(kw => text.toLowerCase().includes(kw))) {
      confetti({
        particleCount: 160,
        spread: 80,
        origin: { y: 0.7 },
        colors: ["#818cf8", "#a78bfa", "#c084fc", "#f472b6", "#60a5fa"],
      });
    }

    const userMessage: Message     = { role: "user", content: text };
    const historyBeforeMessage      = [...messages];
    const updatedMessages           = [...messages, userMessage];
    setMessages(updatedMessages);
    setIsStreaming(true);
    setStreamingContent("");
    setSuggestions([]);
    setThinkingStatus(null);

    const controller = new AbortController();
    abortRef.current = controller;
    let fullResponse = "";

    try {
      const gen = streamChatEvents(text, historyBeforeMessage, controller.signal);
      for await (const event of gen) {
        if (event.type === "status") {
          setThinkingStatus(event.text);
        } else if (event.type === "token") {
          setThinkingStatus(null);
          fullResponse = event.text;
          setStreamingContent(fullResponse);
        } else if (event.type === "topic") {
          setTopic(event.value);
        } else if (event.type === "suggestions") {
          setSuggestions(event.items);
        } else if (event.type === "error") {
          console.error("Backend error:", event.message);
          fullResponse = fullResponse || "Sorry, I ran into an error. Please try again.";
        }
      }
    } catch (err: unknown) {
      if (!(err instanceof Error && err.name === "AbortError")) {
        fullResponse = fullResponse || "Sorry, something went wrong. Please try again.";
        console.error(err);
      }
    } finally {
      const committed = fullResponse || "Sorry, something went wrong. Please try again.";
      setMessages([...updatedMessages, { role: "assistant", content: committed }]);
      setNewMessageIndex(updatedMessages.length);
      setStreamingContent("");
      setThinkingStatus(null);
      setIsStreaming(false);
      setTimeout(() => setNewMessageIndex(null), 2000);
    }
  }, [messages, isStreaming]);

  const exportChat = useCallback(() => {
    if (messages.length === 0) return;
    const header = `# Conversation with Hoang's Personal AI\n_Exported ${new Date().toLocaleDateString()}_\n\n---\n\n`;
    const body   = messages
      .map(m => `**${m.role === "user" ? "You" : "Hoang's AI"}:** ${m.content}`)
      .join("\n\n");
    const blob = new Blob([header + body], { type: "text/markdown" });
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement("a");
    a.href     = url;
    a.download = `hoang-ai-chat-${Date.now()}.md`;
    a.click();
    URL.revokeObjectURL(url);
  }, [messages]);

  const isEmpty = messages.length === 0 && !isStreaming;

  return (
    // ── Root shell ──────────────────────────────────────────
    <div className="flex flex-col h-screen bg-zinc-950 text-zinc-100 relative overflow-hidden">

      {/* ── Gradient blobs (fixed, behind everything) ── */}
      <div className="fixed inset-0 pointer-events-none" style={{ zIndex: 0 }}>
        <div
          className="blob-a absolute w-[700px] h-[700px] rounded-full blur-3xl"
          style={{
            background: `radial-gradient(circle, ${hexToRgba(blobA, 0.40)} 0%, transparent 70%)`,
            top: "-220px",
            right: "-180px",
            transition: "background 1.2s ease",
          }}
        />
        <div
          className="blob-b absolute w-[500px] h-[500px] rounded-full blur-3xl"
          style={{
            background: `radial-gradient(circle, ${hexToRgba(blobB, 0.30)} 0%, transparent 70%)`,
            bottom: "-150px",
            left: "-120px",
            transition: "background 1.2s ease",
          }}
        />
      </div>

      {/* ── All visible UI (above gradient) ── */}
      <div className="relative flex flex-col h-full" style={{ zIndex: 1 }}>

        {/* Header */}
        <header className="flex items-center gap-3 px-5 py-3.5 border-b border-zinc-800 bg-zinc-900/80 backdrop-blur-sm flex-shrink-0">
          <div className={`w-8 h-8 rounded-full ${topicColor} flex items-center justify-center text-xs font-bold text-white flex-shrink-0 transition-colors duration-500`}>
            HL
          </div>
          <div>
            <h1 className="text-sm font-semibold text-white">Hoang Nhat Duy Le</h1>
            <p className="text-xs text-zinc-400">Personal AI Assistant · MES Software Engineer @ First Solar</p>
          </div>
          <div className="ml-auto flex items-center gap-3">
            {messages.length > 0 && (
              <button
                onClick={exportChat}
                title="Export conversation as Markdown"
                className="text-xs text-zinc-500 hover:text-zinc-300 transition-colors flex items-center gap-1.5 border border-zinc-700 hover:border-zinc-600 px-2.5 py-1 rounded-lg"
              >
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-3.5 h-3.5">
                  <path d="M10.75 2.75a.75.75 0 00-1.5 0v8.614L6.295 8.235a.75.75 0 10-1.09 1.03l4.25 4.5a.75.75 0 001.09 0l4.25-4.5a.75.75 0 00-1.09-1.03l-2.955 3.129V2.75z" />
                  <path d="M3.5 12.75a.75.75 0 00-1.5 0v2.5A2.75 2.75 0 004.75 18h10.5A2.75 2.75 0 0018 15.25v-2.5a.75.75 0 00-1.5 0v2.5c0 .69-.56 1.25-1.25 1.25H4.75c-.69 0-1.25-.56-1.25-1.25v-2.5z" />
                </svg>
                Export
              </button>
            )}
            <div className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
              <span className="text-xs text-zinc-500">Online</span>
            </div>
          </div>
        </header>

        {/* Chat + sidebar row */}
        <div className="flex flex-1 overflow-hidden">

          {/* Chat column */}
          <div className="flex flex-col flex-1 overflow-hidden">
              {isEmpty ? (
                <div className="flex flex-col flex-1 items-center justify-center px-6 pb-4">
                  <div className={`w-16 h-16 rounded-full bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center mb-4`}>
                    <span className="text-2xl font-bold text-indigo-400">H</span>
                  </div>
                  <h2 className="text-xl font-semibold text-white mb-1">Ask me about Hoang</h2>
                  <p className="text-sm text-zinc-400 text-center max-w-sm mb-6">
                    I have access to his full career history, projects, skills, and GitHub repositories.
                  </p>
                  <StarterQuestions onSelect={sendMessage} />
                </div>
              ) : (
                <ChatWindow
                  messages={messages}
                  streamingContent={streamingContent}
                  isStreaming={isStreaming}
                  thinkingStatus={thinkingStatus}
                  suggestions={suggestions}
                  newMessageIndex={newMessageIndex}
                  topicColor={topicColor}
                  onSuggestionSelect={sendMessage}
                />
              )}
              <InputBar
                onSend={sendMessage}
                disabled={isStreaming}
                isStreaming={isStreaming}
                onCancel={cancelStream}
                lastUserMessage={lastUserMessage}
              />
          </div>

          {/* Desktop sidebar */}
          <aside className="hidden lg:flex flex-col w-72 border-l border-zinc-800 bg-zinc-900/40 flex-shrink-0 overflow-hidden">
            <ProfileCard topic={topic} />
          </aside>

        </div>{/* end chat + sidebar row */}

        {/* Mobile: floating HL button */}
        <button
          onClick={() => setSheetOpen(true)}
          className={`fixed bottom-24 right-4 z-30 lg:hidden w-11 h-11 rounded-full ${topicColor} shadow-lg flex items-center justify-center text-xs font-bold text-white transition-all duration-500 hover:scale-110 active:scale-95`}
          title="View profile"
          aria-label="Open profile card"
        >
          HL
        </button>

        {/* Mobile: bottom sheet */}
        <ProfileSheet
          topic={topic}
          topicColor={topicColor}
          isOpen={sheetOpen}
          onClose={() => setSheetOpen(false)}
        />

      </div>{/* end visible UI wrapper */}

    </div>
  );
}
