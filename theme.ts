// Corporate design theme switching for Svelte / SvelteKit.
// Applies `data-theme="light" | "dark"` to <html> and persists the choice.
// Call initTheme() once on the client (e.g. in your root layout) — the store
// only touches the DOM after that, so importing has no hidden side effects.

import { writable } from 'svelte/store';

export type Theme = 'light' | 'dark';

const STORAGE_KEY = 'cd-theme';

export const theme = writable<Theme>('light');

let started = false;

function storedTheme(): Theme | null {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    return stored === 'light' || stored === 'dark' ? stored : null;
  } catch {
    // storage disabled/blocked (private mode, cookie partition) — fall back to the system pref
    return null;
  }
}

/** Reads the stored or system preference, applies it, and wires persistence. */
export function initTheme(): Theme {
  if (typeof document === 'undefined') return 'light';
  const initial =
    storedTheme() ??
    (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
  theme.set(initial);
  if (!started) {
    started = true;
    theme.subscribe((value) => {
      document.documentElement.dataset.theme = value;
      try {
        localStorage.setItem(STORAGE_KEY, value);
      } catch {
        // e.g. storage disabled — the theme still applies for this session.
      }
    });
  }
  return initial;
}

export function toggleTheme(): void {
  theme.update((t) => (t === 'light' ? 'dark' : 'light'));
}

export function setTheme(value: Theme): void {
  theme.set(value);
}
