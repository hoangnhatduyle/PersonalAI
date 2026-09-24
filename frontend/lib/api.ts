export interface Message {
  role: "user" | "assistant";
  content: string;
  sources?: string[];
  clientMessageId?: string;
}

export type StreamEvent =
  | { type: "status"; text: string }
  | { type: "token"; text: string }
  | { type: "topic"; value: string }
  | { type: "suggestions"; items: string[] }
  | { type: "contact_ask"; question: string }
  | { type: "contact_resolved"; name?: string; email?: string; declined?: boolean }
  | { type: "response_id"; value: string }
  | { type: "sources"; items: string[] }
  | { type: "error"; message: string };

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:7860";

/** Ping the backend health endpoint. Resolves true if alive, false otherwise. */
export async function pingBackend(): Promise<boolean> {
  try {
    const res = await fetch(`${API_URL}/api/health`, { cache: "no-store" });
    return res.ok;
  } catch {
    return false;
  }
}

/** Resolve (or silently auto-resolve) a pending contact-info ask. Returns true on success. */
export async function resolveContact(payload: {
  question: string;
  name?: string;
  email?: string;
  declined?: boolean;
}): Promise<boolean> {
  try {
    const res = await fetch(`${API_URL}/api/resolve-contact`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    return res.ok;
  } catch {
    return false;
  }
}

/** Submit thumbs up/down feedback for a previously logged assistant message. Returns true on success. */
export async function submitFeedback(clientMessageId: string, value: "up" | "down"): Promise<boolean> {
  try {
    const res = await fetch(`${API_URL}/api/feedback`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ client_message_id: clientMessageId, value }),
    });
    return res.ok;
  } catch {
    return false;
  }
}

/**
 * Stream typed events from the Personal AI backend via SSE.
 * Yields strongly-typed StreamEvent objects.
 */
export async function* streamChatEvents(
  message: string,
  opts: {
    previousResponseId?: string | null;
    regenerate?: boolean;
    clientMessageId: string;
    signal?: AbortSignal;
  }
): AsyncGenerator<StreamEvent> {
  const response = await fetch(`${API_URL}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message,
      previous_response_id: opts.previousResponseId ?? null,
      regenerate: opts.regenerate ?? false,
      client_message_id: opts.clientMessageId,
    }),
    signal: opts.signal,
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status} ${response.statusText}`);
  }

  const reader = response.body!.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() ?? "";

    for (const line of lines) {
      if (!line.startsWith("data: ")) continue;
      const data = line.slice(6).trim();
      if (data === "[DONE]") return;
      try {
        yield JSON.parse(data) as StreamEvent;
      } catch {
        // ignore malformed SSE lines
      }
    }
  }
}
