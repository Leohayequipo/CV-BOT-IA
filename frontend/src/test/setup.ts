import '@testing-library/jest-dom/vitest';
import { cleanup } from '@testing-library/react';
import { afterAll, afterEach, beforeAll } from 'vitest';
import { server } from './server';

// Vitest runs without globals, so Testing Library can't register its own cleanup
afterEach(cleanup);
// The theme and the language a test picks don't carry over to the next one
afterEach(() => localStorage.clear());

// Every request goes to the fake API; one it doesn't know fails the test
beforeAll(() => server.listen({ onUnhandledFrame: 'error' }));
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

// jsdom has no canvas; axe asks for one to look at icon fonts and copes without it
HTMLCanvasElement.prototype.getContext = () => null;

// jsdom has no matchMedia; this one answers the colour scheme and the layout. Tests run on
// desktop unless they ask for a phone
let systemTheme: 'light' | 'dark' = 'light';
let viewport: 'desktop' | 'phone' = 'desktop';

export function setSystemTheme(theme: 'light' | 'dark'): void {
  systemTheme = theme;
}

export function setViewport(size: 'desktop' | 'phone'): void {
  viewport = size;
}

afterEach(() => setViewport('desktop'));

window.matchMedia = (query: string): MediaQueryList => ({
  matches:
    (query === '(prefers-color-scheme: dark)' && systemTheme === 'dark') ||
    (query === '(min-width: 768px)' && viewport === 'desktop'),
  media: query,
  onchange: null,
  addEventListener: () => undefined,
  removeEventListener: () => undefined,
  addListener: () => undefined,
  removeListener: () => undefined,
  dispatchEvent: () => false,
});
