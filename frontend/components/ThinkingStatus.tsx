interface Props {
  status: string;
  topicColor: string;
}

export default function ThinkingStatus({ status, topicColor }: Props) {
  return (
    <div className="flex gap-3 thinking-animate">
      {/* Avatar */}
      <div className={`flex-shrink-0 w-8 h-8 rounded-full ${topicColor} flex items-center justify-center text-sm font-semibold text-white transition-colors duration-500`}>
        AI
      </div>
      {/* Status bubble */}
      <div className="px-4 py-2.5 rounded-2xl rounded-tl-sm bg-zinc-800/80 border border-zinc-700 flex items-center gap-2.5 text-xs text-zinc-400">
        <span className="flex gap-1">
          <span className="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce [animation-delay:-0.3s]" />
          <span className="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce [animation-delay:-0.15s]" />
          <span className="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce" />
        </span>
        <span className="text-zinc-400">{status}</span>
      </div>
    </div>
  );
}
