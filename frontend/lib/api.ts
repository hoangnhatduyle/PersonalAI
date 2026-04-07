export interface Message {
  role: "user" | "assistant";
  content: string;
}

export type StreamEvent =
  | { type: "status"; text: string }
  | { type: "token"; text: string }
  | { type: "topic"; value: string }
  | { type: "suggestions"; items: string[] }
  | { type: "error"; message: string };

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:7860";

/**
 * Stream typed events from the Personal AI backend via SSE.
 * Yields strongly-typed StreamEvent objects.
 */
export async function* streamChatEvents(
  message: string,
  history: Message[],
  signal?: AbortSignal
): AsyncGenerator<StreamEvent> {
  const response = await fetch(`${API_URL}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, history }),
    signal,
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
