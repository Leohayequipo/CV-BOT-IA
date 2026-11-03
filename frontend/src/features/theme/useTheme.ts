import { useCallback, useEffect, useState, useSyncExternalStore } from 'react';

export type Theme = 'light' | 'dark';

// index.html reads the same key before the first paint, so a chosen theme never flashes
const STORAGE_KEY = 'theme';
const DARK_QUERY = '(prefers-color-scheme: dark)';

/**
 * The theme follows the OS until the visitor picks one; the choice is kept on this device.
 * tokens.css switches every colour from the data-theme attribute on <html>.
 */
export function useTheme() {
  const systemIsDark = useSyncExternalStore(
    subscribeToSystem,
    () => matchMedia(DARK_QUERY).matches,
  );
  const [chosen, setChosen] = useState<Theme | null>(readChoice);
  const theme: Theme = chosen ?? (systemIsDark ? 'dark' : 'light');

  useEffect(() => {
    if (chosen === null) return;
    document.documentElement.dataset.theme = chosen;
    saveChoice(chosen);
  }, [chosen]);

  const toggleTheme = useCallback(() => setChosen(theme === 'dark' ? 'light' : 'dark'), [theme]);

  return { theme, toggleTheme };
}

function subscribeToSystem(onChange: () => void): () => void {
  const query = matchMedia(DARK_QUERY);
  query.addEventListener('change', onChange);
  return () => query.removeEventListener('change', onChange);
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
