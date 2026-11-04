import { Check } from 'lucide-react';
import { useI18n } from '../../../i18n/useI18n';
import { formatTime } from '../time';
import { CardFrame } from './CardFrame';

/** After the visitor confirms: the message reached Leonardo. */
export function MessageSentCard({ at }: { at: Date }) {
  const { messages, locale } = useI18n();
  const { cards } = messages;
  return (
    <CardFrame className="flex items-start gap-3 px-4 py-3.5">
      <span
        aria-hidden="true"
        className="flex size-10 shrink-0 items-center justify-center rounded-full bg-accent-soft text-accent motion-safe:animate-pop"
      >
        <Check size={20} className="motion-safe:animate-draw" />
      </span>
      <div className="min-w-0">
        <h3 className="text-card-title font-semibold">{cards.sentTitle}</h3>
        <p className="mt-0.5 text-small text-muted">{cards.sentLine}</p>
        <p className="mt-1 text-label text-muted">
          <time dateTime={at.toISOString()}>{cards.sentToday(formatTime(at, locale))}</time>
        </p>
      </div>
    </CardFrame>
  );
}
