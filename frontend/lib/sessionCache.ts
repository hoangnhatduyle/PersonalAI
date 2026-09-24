const STORAGE_KEY = "personalai_session";
const IDLE_TIMEOUT_MS = 3_600_000; // 1 hour

interface SessionState {
  previousResponseId: string;
  lastActivity: number;
}

/** Read the cached previous_response_id, if any. Null on first visit, idle timeout, or storage unavailable. */
export function getPreviousResponseId(): string | null {
  try {
    const raw = window.sessionStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    const state = JSON.parse(raw) as SessionState;
    if (Date.now() - state.lastActivity > IDLE_TIMEOUT_MS) {
      window.sessionStorage.removeItem(STORAGE_KEY);
      return null;
    }
    return state.previousResponseId;
  } catch {
    return null;
  }
}

/** Cache the latest response id and refresh the idle timer. */
export function setPreviousResponseId(id: string): void {
  try {
    const state: SessionState = { previousResponseId: id, lastActivity: Date.now() };
    window.sessionStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  } catch {
    // private browsing / storage disabled — silently no-op
  }
}
