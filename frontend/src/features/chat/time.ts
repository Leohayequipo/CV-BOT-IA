import type { Locale } from '../../i18n';

const clocks = new Map<Locale, Intl.DateTimeFormat>();

/** The time of day a message was sent or confirmed, as the chat shows it. */
export function formatTime(date: Date, locale: Locale): string {
  let clock = clocks.get(locale);
  if (!clock) {
    clock = new Intl.DateTimeFormat(locale, { hour: '2-digit', minute: '2-digit' });
    clocks.set(locale, clock);
  }
  return clock.format(date);
}
