import { type ReactNode, useEffect, useMemo, useState } from 'react';
import { I18nContext } from './context';
import { catalogs, type Locale, pickLocale } from './index';

const STORAGE_KEY = 'locale';

/** Follows the browser until the visitor picks a language, which is kept on this device. */
export function I18nProvider({ children }: { children: ReactNode }) {
  const [locale, setLocale] = useState<Locale>(
    () => readChoice() ?? pickLocale(navigator.languages),
  );

  useEffect(() => {
    // Screen readers and search engines read the page in its language
    document.documentElement.lang = locale;
  }, [locale]);

  const value = useMemo(
    () => ({
      locale,
      messages: catalogs[locale],
      setLocale: (next: Locale) => {
        setLocale(next);
        saveChoice(next);
      },
    }),
    [locale],
  );
  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
}

// Storage can be unavailable (private browsing, blocked cookies): the choice then lasts the visit
function readChoice(): Locale | null {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    return stored === 'en' || stored === 'es' ? stored : null;
  } catch {
    return null;
  }
}

function saveChoice(locale: Locale): void {
  try {
    localStorage.setItem(STORAGE_KEY, locale);
  } catch {
    // The language still applies until the page closes
  }
}
