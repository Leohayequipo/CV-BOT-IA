import { en, type Messages } from './en';
import { es } from './es';

export type { Messages };
export type Locale = 'en' | 'es';

export const catalogs: Record<Locale, Messages> = { en, es };

/**
 * English by default; Spanish when the browser prefers it to English (ADR-015). The first
 * language in the visitor's list that the site speaks wins.
 */
export function pickLocale(languages: readonly string[]): Locale {
  for (const language of languages) {
    const code = language.toLowerCase().split('-')[0];
    if (code === 'en' || code === 'es') return code;
  }
  return 'en';
}
