"use client";

import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { fetchConversations, type LoggedConversation } from "@/lib/adminApi";
import { setAdminToken, useAdminToken } from "@/lib/adminToken";

const LIMIT = 20;
const RANGE_OPTIONS: { label: string; days: 3 | 7 | 30 | 90 }[] = [
  { label: "3d", days: 3 },
  { label: "7d", days: 7 },
  { label: "1 month", days: 30 },
  { label: "3 months", days: 90 },
];

function sinceForDays(days: number): string {
  return new Date(Date.now() - days * 86_400_000).toISOString();
}

function formatTimestamp(iso: string): string {
  return new Date(iso).toLocaleString(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

function LoginForm({ onSubmit }: { onSubmit: (token: string) => void }) {
  const [value, setValue] = useState("");

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        onSubmit(value.trim());
      }}
      className="flex flex-col gap-3 w-full max-w-xs"
    >
      <input
        type="password"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder="Admin token"
        autoFocus
        className="bg-zinc-900 border border-zinc-700 rounded-lg px-3 py-2 text-sm text-white placeholder:text-zinc-600 focus:outline-none focus:border-indigo-500"
      />
      <button
        type="submit"
        disabled={!value.trim()}
        className="bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 disabled:hover:bg-indigo-600 transition-colors rounded-lg px-3 py-2 text-sm font-medium text-white"
      >
        Enter
      </button>
    </form>
  );
}

function ConversationRow({ item }: { item: LoggedConversation }) {
  return (
    <div className="bg-zinc-800/60 border border-zinc-700/50 rounded-2xl p-4">
      <div className="flex items-center justify-between gap-2 mb-3">
        <span className="text-[11px] text-zinc-500">{formatTimestamp(item.created_at)}</span>
        {item.topic && (
          <span className="text-xs px-2 py-0.5 rounded-full bg-indigo-900/60 text-indigo-300 border border-indigo-700/40 font-medium">
            {item.topic}
          </span>
        )}
      </div>
      <div className="space-y-2">
        <div>
          <p className="text-[10px] font-semibold text-zinc-500 uppercase tracking-wider mb-1">User</p>
          <p className="text-sm text-zinc-200 whitespace-pre-wrap">{item.user_message}</p>
        </div>
        <div>
          <p className="text-[10px] font-semibold text-zinc-500 uppercase tracking-wider mb-1">Assistant</p>
          <div
            className="prose prose-sm prose-invert max-w-none text-zinc-400
              prose-p:my-1 prose-p:leading-relaxed prose-ul:my-1 prose-ul:pl-4
              prose-ol:my-1 prose-ol:pl-4 prose-li:my-0.5 prose-strong:text-white
              prose-headings:text-white prose-headings:font-semibold
              prose-a:text-indigo-400 prose-a:no-underline hover:prose-a:underline"
          >
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{item.assistant_response}</ReactMarkdown>
          </div>
        </div>
      </div>
    </div>
  );
}

interface LoadedPage {
  /** Identifies the request this page answers (token, search, range, page). */
  key: string;
  items: LoggedConversation[];
  total: number;
  error: string | null;
}

export default function AdminPage() {
  const token = useAdminToken();
  const [loaded, setLoaded] = useState<LoadedPage | null>(null);
  const [query, setQuery] = useState("");
  const [debouncedQuery, setDebouncedQuery] = useState("");
  const [rangeDays, setRangeDays] = useState<3 | 7 | 30 | 90>(7);
  const [page, setPage] = useState(0);

  useEffect(() => {
    const t = setTimeout(() => {
      setDebouncedQuery(query);
      setPage(0);
    }, 300);
    return () => clearTimeout(t);
  }, [query]);

  // Loading, items and error are derived from "has the response for the current request arrived?",
  // so no state is set synchronously inside the effect, and a slow stale response can never
  // overwrite a newer one.
  const requestKey = token ? `${token}|${debouncedQuery}|${rangeDays}|${page}` : null;
  const loading = requestKey !== null && loaded?.key !== requestKey;
  const items = loaded?.items ?? [];
  const total = loaded?.total ?? 0;
  const error = loaded && (requestKey === null || loaded.key === requestKey) ? loaded.error : null;

  useEffect(() => {
    if (!token || !requestKey) return;
    let cancelled = false;
    fetchConversations(token, {
      q: debouncedQuery || undefined,
      since: sinceForDays(rangeDays),
      limit: LIMIT,
      offset: page * LIMIT,
    })
      .then((res) => {
        if (!cancelled) setLoaded({ key: requestKey, items: res.items, total: res.total, error: null });
      })
      .catch((err: Error) => {
        if (cancelled) return;
        // keep whatever was on screen, and show the error
        setLoaded((prev) => ({
          key: requestKey,
          items: prev?.items ?? [],
          total: prev?.total ?? 0,
          error: err.message,
        }));
        if (err.message === "Invalid token") setAdminToken(null);
      });
    return () => {
      cancelled = true;
    };
  }, [token, requestKey, debouncedQuery, rangeDays, page]);

  const handleLogin = (candidate: string) => setAdminToken(candidate);

  if (!token) {
    return (
      <div className="min-h-screen bg-zinc-950 flex items-center justify-center p-6">
        <div className="flex flex-col items-center gap-3">
          <LoginForm onSubmit={handleLogin} />
          {error && <p className="text-sm text-rose-400">{error}</p>}
        </div>
      </div>
    );
  }

  const totalPages = Math.max(1, Math.ceil(total / LIMIT));

  return (
    <div className="min-h-screen bg-zinc-950 text-white p-6 max-w-3xl mx-auto">
      <h1 className="text-lg font-semibold mb-4">Conversation Log</h1>

      <div className="flex flex-wrap items-center gap-2 mb-4">
        {RANGE_OPTIONS.map((opt) => (
          <button
            key={opt.days}
            onClick={() => {
              setRangeDays(opt.days);
              setPage(0);
            }}
            className={`text-xs px-3 py-1.5 rounded-full border transition-colors ${
              rangeDays === opt.days
                ? "bg-indigo-600 border-indigo-500 text-white"
                : "bg-zinc-900 border-zinc-700 text-zinc-400 hover:text-white"
            }`}
          >
            {opt.label}
          </button>
        ))}
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search..."
          className="ml-auto bg-zinc-900 border border-zinc-700 rounded-lg px-3 py-1.5 text-sm text-white placeholder:text-zinc-600 focus:outline-none focus:border-indigo-500 min-w-[160px]"
        />
      </div>

      {error && <p className="text-sm text-rose-400 mb-4">{error}</p>}

      {loading ? (
        <p className="text-sm text-zinc-500">Loading...</p>
      ) : items.length === 0 ? (
        <p className="text-sm text-zinc-500">No conversations found.</p>
      ) : (
        <div className="space-y-3">
          {items.map((item) => (
            <ConversationRow key={item.id} item={item} />
          ))}
        </div>
      )}

      <div className="flex items-center justify-between mt-6">
        <button
          onClick={() => setPage((p) => Math.max(0, p - 1))}
          disabled={page === 0}
          className="text-xs px-3 py-1.5 rounded-lg bg-zinc-900 border border-zinc-700 text-zinc-300 disabled:opacity-40 hover:text-white transition-colors"
        >
          Previous
        </button>
        <span className="text-xs text-zinc-500">
          Page {page + 1} of {totalPages}
        </span>
        <button
          onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
          disabled={page + 1 >= totalPages}
          className="text-xs px-3 py-1.5 rounded-lg bg-zinc-900 border border-zinc-700 text-zinc-300 disabled:opacity-40 hover:text-white transition-colors"
        >
          Next
        </button>
      </div>
    </div>
  );
}
