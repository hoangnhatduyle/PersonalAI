export type ContactPreference =
  | { status: "given"; name?: string; email?: string }
  | { status: "declined" };

const STORAGE_KEY = "personalai_contact_pref";

/** Read the visitor's cached contact preference, if any. Null on first visit or if storage is unavailable. */
export function getContactPreference(): ContactPreference | null {
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    return raw ? (JSON.parse(raw) as ContactPreference) : null;
  } catch {
    return null;
  }
}

/** Cache the visitor's contact preference so later unknown questions auto-resolve without asking again. */
export function setContactPreference(pref: ContactPreference): void {
  try {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(pref));
  } catch {
    // private browsing / storage disabled — silently no-op
  }
}
