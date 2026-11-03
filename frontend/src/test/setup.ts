import '@testing-library/jest-dom/vitest';
import { cleanup } from '@testing-library/react';
import { afterEach } from 'vitest';

// Vitest runs without globals, so Testing Library can't register its own cleanup
afterEach(cleanup);

// jsdom has no matchMedia; this one answers the colour-scheme query the theme reads
let systemTheme: 'light' | 'dark' = 'light';

export function setSystemTheme(theme: 'light' | 'dark'): void {
  systemTheme = theme;
}

window.matchMedia = (query: string): MediaQueryList => ({
  matches: query === '(prefers-color-scheme: dark)' && systemTheme === 'dark',
  media: query,
  onchange: null,
  addEventListener: () => undefined,
  removeEventListener: () => undefined,
  addListener: () => undefined,
  removeListener: () => undefined,
  dispatchEvent: () => false,
});
