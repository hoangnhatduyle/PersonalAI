import { useSyncExternalStore } from "react";

const STORAGE_KEY = "admin_token";

const listeners = new Set<() => void>();

// Used when sessionStorage is unavailable (private mode, blocked storage): the token still works for
// this page session, it just does not persist across reloads.
let memoryToken: string | null = null;

function readToken(): string | null {
  try {
    return sessionStorage.getItem(STORAGE_KEY) ?? memoryToken;
  } catch {
    return memoryToken;
  }
}

function subscribe(onChange: () => void): () => void {
  listeners.add(onChange);
  window.addEventListener("storage", onChange); // other tabs
  return () => {
    listeners.delete(onChange);
    window.removeEventListener("storage", onChange);
  };
}

/** Save (or clear, with null) the admin token and notify every component reading it. */
export function setAdminToken(value: string | null): void {
  memoryToken = value;
  try {
    if (value === null) sessionStorage.removeItem(STORAGE_KEY);
    else sessionStorage.setItem(STORAGE_KEY, value);
  } catch {
    // storage unavailable: the in-memory copy above is enough for this session
  }
  listeners.forEach((notify) => notify());
}

/**
 * The current admin token, or null. Server render and the first client render both see null, then the
 * stored value is applied, so there is no hydration mismatch and no setState inside an effect.
 */
export function useAdminToken(): string | null {
  return useSyncExternalStore(subscribe, readToken, () => null);
}
