import { CircleAlert, Clock, RotateCcw } from 'lucide-react';
import { messages } from '../../i18n';
import type { ChatError } from './api';

/** Takes the place of an answer that failed. Every error message reads "what happened. What
 * to do.", so the first sentence becomes the title. */
export function ErrorNotice({ error, onRetry }: { error: ChatError; onRetry: () => void }) {
  const text = error.message || messages.chat.networkError;
  const [title = text, ...rest] = text.split(/(?<=\.)\s+/);
  return (
    <div
      role="alert"
      className="mt-1.5 flex max-w-[460px] items-start gap-2.5 rounded-card border border-border bg-card px-3.5 py-3"
    >
      <CircleAlert size={18} aria-hidden="true" className="mt-px shrink-0 text-danger" />
      <div className="min-w-0 flex-1">
        <p className="font-semibold">{title}</p>
        {rest.length > 0 && <p className="mt-0.5 text-muted">{rest.join(' ')}</p>}
        <button
          type="button"
          onClick={onRetry}
          className="mt-2.5 inline-flex h-9 items-center gap-1.5 rounded-full border border-accent px-3.5 text-small font-semibold text-accent hover:bg-accent-soft"
        >
          <RotateCcw size={16} aria-hidden="true" />
          {messages.chat.retry}
        </button>
      </div>
    </div>
  );
}

/** Above the disabled question box while the question limit applies. */
export function LimitNotice() {
  return (
    <output className="mx-3.5 mb-2.5 flex items-start gap-2.5 rounded-card border border-border bg-subtle px-3 py-2.5 text-small md:mx-4">
      <Clock size={18} aria-hidden="true" className="mt-px shrink-0 text-muted" />
      <span>{messages.chat.limit}</span>
    </output>
  );
}
