import { locale } from '../../i18n';

const clock = new Intl.DateTimeFormat(locale, { hour: '2-digit', minute: '2-digit' });

/** The time of day a message was sent or confirmed, as the chat shows it. */
export function formatTime(date: Date): string {
  return clock.format(date);
}
