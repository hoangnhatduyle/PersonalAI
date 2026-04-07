export default function TypingIndicator() {
  return (
    <div className="flex gap-3 flex-row">
      {/* Avatar */}
      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-zinc-700 flex items-center justify-center text-sm font-semibold text-indigo-300">
        AI
      </div>
      {/* Bubble */}
      <div className="px-4 py-3 rounded-2xl rounded-tl-sm bg-zinc-800 border border-zinc-700 flex items-center gap-1.5">
        <span className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce [animation-delay:-0.3s]" />
        <span className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce [animation-delay:-0.15s]" />
        <span className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" />
      </div>
    </div>
  );
}
