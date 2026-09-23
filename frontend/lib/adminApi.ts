const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:7860";

export interface LoggedConversation {
  id: number;
  created_at: string;
  user_message: string;
  assistant_response: string;
  topic: string | null;
}

export interface ConversationPage {
  items: LoggedConversation[];
  total: number;
}

export async function fetchConversations(
  token: string,
  opts: { q?: string; since?: string; limit: number; offset: number }
): Promise<ConversationPage> {
  const params = new URLSearchParams({ limit: String(opts.limit), offset: String(opts.offset) });
  if (opts.q) params.set("q", opts.q);
  if (opts.since) params.set("since", opts.since);
  const res = await fetch(`${API_URL}/api/admin/conversations?${params}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error(res.status === 401 ? "Invalid token" : "Failed to load");
  return res.json();
}
