import '@testing-library/jest-dom/vitest';
import { cleanup } from '@testing-library/react';
import { afterAll, afterEach, beforeAll } from 'vitest';
import { server } from './server';

// Vitest runs without globals, so Testing Library can't register its own cleanup
afterEach(cleanup);

// Every request goes to the fake API; one it doesn't know fails the test
beforeAll(() => server.listen({ onUnhandledFrame: 'error' }));
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

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
