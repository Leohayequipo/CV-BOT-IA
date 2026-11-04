import { useCallback, useEffect, useState } from 'react';
import { useMediaQuery } from '../../lib/useMediaQuery';

export type Theme = 'light' | 'dark';

// index.html reads the same key before the first paint, so a chosen theme never flashes
const STORAGE_KEY = 'theme';
const DARK_QUERY = '(prefers-color-scheme: dark)';

/**
 * The theme follows the OS until the visitor picks one; the choice is kept on this device.
 * tokens.css switches every colour from the data-theme attribute on <html>.
 */
export function useTheme() {
  const systemIsDark = useMediaQuery(DARK_QUERY);
  const [chosen, setChosen] = useState<Theme | null>(readChoice);
  const theme: Theme = chosen ?? (systemIsDark ? 'dark' : 'light');

  useEffect(() => {
    if (chosen === null) return;
    const root = document.documentElement;
    // The colours change at once: no button fades between themes (DESIGN.md)
    root.classList.add('theme-switching');
    root.dataset.theme = chosen;
    saveChoice(chosen);
    const frame = requestAnimationFrame(() =>
      requestAnimationFrame(() => root.classList.remove('theme-switching')),
    );
    return () => cancelAnimationFrame(frame);
  }, [chosen]);

  const toggleTheme = useCallback(() => setChosen(theme === 'dark' ? 'light' : 'dark'), [theme]);

  return { theme, toggleTheme };
}

// Storage can be unavailable (private browsing, blocked cookies): the theme then lasts the visit
function readChoice(): Theme | null {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    return stored === 'light' || stored === 'dark' ? stored : null;
  } catch {
    return null;
  }
}

function saveChoice(theme: Theme): void {
  try {
    localStorage.setItem(STORAGE_KEY, theme);
  } catch {
    // Nothing to do: the theme still applies until the page closes
  }
}
