const STARTERS = [
  "What are you currently working on?",
  "Tell me about the Trading Platform project",
  "What's your educational background?",
  "What tech stack do you use?",
  "What are your career goals?",
  "What did your annual review say?",
];

interface Props {
  onSelect: (question: string) => void;
}

export default function StarterQuestions({ onSelect }: Props) {
  return (
    <div className="w-full max-w-xl mx-auto">
      <p className="text-xs text-zinc-500 text-center mb-3">Try asking…</p>
      <div className="grid grid-cols-2 gap-2">
        {STARTERS.map((q) => (
          <button
            key={q}
            onClick={() => onSelect(q)}
            className="text-left text-xs px-3 py-2.5 rounded-xl border border-zinc-700 bg-zinc-800/60
                       text-zinc-300 hover:bg-zinc-800 hover:text-white hover:border-indigo-500/60
                       transition-all duration-150 leading-relaxed"
          >
            {q}
          </button>
        ))}
      </div>
    </div>
  );
}
