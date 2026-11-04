import { ArrowUp, Check, Mail, Pencil } from 'lucide-react';
import { useEffect, useRef, useState } from 'react';
import { useI18n } from '../../../i18n/useI18n';
import { ChatRequestError } from '../api';
import { formatTime } from '../time';
import { CardFrame } from './CardFrame';
import type { ContactSummaryData } from './cardData';

export type ContactActions = {
  confirmedAt: Date | null;
  onConfirm: (contact: ContactSummaryData) => Promise<void>;
  onCorrect: () => void;
};

/**
 * What the visitor wants to send to Leonardo, to check before it goes. Nothing is sent until
 * they press "Send message" (ADR-021).
 */
export function ContactSummaryCard({
  data,
  actions,
}: {
  data: ContactSummaryData;
  actions: ContactActions;
}) {
  const { messages, locale } = useI18n();
  const { cards } = messages;
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const confirmation = useRef<HTMLOutputElement>(null);
  const confirmedHere = useRef(false);

  // The buttons disappear once it's sent: keep the keyboard focus on what replaced them
  useEffect(() => {
    if (actions.confirmedAt && confirmedHere.current) confirmation.current?.focus();
  }, [actions.confirmedAt]);

  async function confirm() {
    setSending(true);
    setError(null);
    try {
      confirmedHere.current = true;
      await actions.onConfirm(data);
    } catch (failure) {
      confirmedHere.current = false;
      setError(failure instanceof ChatRequestError ? failure.message : messages.chat.networkError);
    } finally {
      setSending(false);
    }
  }

  const from = data.company ? `${data.name} · ${data.company}` : data.name;
  return (
    <CardFrame>
      <div className="flex items-center gap-2.5 border-b border-border px-4 py-3">
        <Mail size={18} aria-hidden="true" className="text-accent" />
        <h3 className="text-card-title font-semibold">{cards.contactTitle}</h3>
      </div>
      <dl className="grid grid-cols-[64px_minmax(0,1fr)] gap-x-3 gap-y-2 px-4 pt-3 pb-3.5 text-[0.84375rem]">
        <dt className="text-muted">{cards.contactFrom}</dt>
        <dd className="min-w-0">{from}</dd>
        <dt className="text-muted">{cards.contactEmail}</dt>
        <dd className="min-w-0 break-words">{data.email}</dd>
        <dt className="text-muted">{cards.contactMessage}</dt>
        <dd className="min-w-0 whitespace-pre-line">{data.message}</dd>
      </dl>
      {actions.confirmedAt ? (
        <output
          ref={confirmation}
          tabIndex={-1}
          className="flex items-center gap-1.5 px-4 pb-3.5 text-small font-semibold text-accent"
        >
          <Check size={16} aria-hidden="true" />
          {cards.contactConfirmed(formatTime(actions.confirmedAt, locale))}
        </output>
      ) : (
        <div className="px-4 pb-3.5">
          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              onClick={() => void confirm()}
              disabled={sending}
              className="inline-flex h-10 items-center gap-2 rounded-full bg-accent px-[18px] font-semibold text-accent-ink hover:brightness-108 disabled:opacity-70"
            >
              <ArrowUp size={18} aria-hidden="true" />
              {sending ? cards.contactSending : cards.contactSend}
            </button>
            <button
              type="button"
              onClick={actions.onCorrect}
              disabled={sending}
              className="inline-flex h-10 items-center gap-2 rounded-full border border-border-strong px-4 font-semibold hover:bg-subtle disabled:opacity-70"
            >
              <Pencil size={16} aria-hidden="true" />
              {cards.contactCorrect}
            </button>
          </div>
          {error && (
            <p role="alert" className="mt-2.5 text-small text-danger">
              {error}
            </p>
          )}
        </div>
      )}
      <p className="border-t border-border px-4 py-2.5 text-label text-muted">
        {cards.contactPrivacy}
      </p>
    </CardFrame>
  );
}
