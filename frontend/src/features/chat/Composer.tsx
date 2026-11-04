import { ArrowUp, FileText, Mail, Square } from 'lucide-react';
import {
  type ChangeEvent,
  type FormEvent,
  type KeyboardEvent,
  useId,
  useRef,
  useState,
} from 'react';
import { useI18n } from '../../i18n/useI18n';
import { useMediaQuery } from '../../lib/useMediaQuery';

// The box grows with the text up to this height, then scrolls (a pasted job offer is long)
const MAX_HEIGHT = 140;

type ComposerProps = {
  busy: boolean;
  limited: boolean;
  onSend: (question: string) => void;
  onStop: () => void;
};

/** The question box. Enter sends, Shift+Enter adds a line, and while an answer streams the
 * send button becomes the stop button. */
export function Composer({ busy, limited, onSend, onStop }: ComposerProps) {
  const { messages } = useI18n();
  // Tailwind's md breakpoint, where the phone layout ends (DESIGN.md)
  const wide = useMediaQuery('(min-width: 768px)');
  const { chat, questions } = messages;
  const inputId = useId();
  const [draft, setDraft] = useState('');
  const input = useRef<HTMLTextAreaElement>(null);

  function onChange(event: ChangeEvent<HTMLTextAreaElement>) {
    const box = event.target;
    setDraft(box.value);
    box.style.height = 'auto';
    box.style.height = `${Math.min(box.scrollHeight, MAX_HEIGHT)}px`;
  }

  function send(event?: FormEvent) {
    event?.preventDefault();
    if (busy || limited || !draft.trim()) return;
    onSend(draft);
    setDraft('');
    if (input.current) {
      // Back to one line
      input.current.style.height = '';
      input.current.focus();
    }
  }

  function onKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    // isComposing: Enter also confirms a word in Japanese or Chinese input methods
    if (event.key === 'Enter' && !event.shiftKey && !event.nativeEvent.isComposing) send(event);
  }

  return (
    <div className="border-t border-border px-3 pt-2.5 pb-4 md:px-4 md:pt-3 md:pb-2.5">
      <form onSubmit={send} className="flex items-end gap-2">
        <label htmlFor={inputId} className="sr-only">
          {chat.questionLabel}
        </label>
        <textarea
          id={inputId}
          ref={input}
          rows={1}
          value={draft}
          disabled={limited}
          onChange={onChange}
          onKeyDown={onKeyDown}
          placeholder={
            limited ? chat.limitedPlaceholder : wide ? chat.placeholder : chat.placeholderShort
          }
          className="block min-h-[46px] min-w-0 flex-1 resize-none rounded-[23px] border border-border-strong bg-card px-[18px] py-3 text-body placeholder:text-muted disabled:border-border disabled:bg-subtle disabled:text-muted"
        />
        {busy ? (
          <button
            type="button"
            onClick={onStop}
            aria-label={chat.stop}
            title={chat.stop}
            className="flex size-[46px] shrink-0 items-center justify-center rounded-full border border-accent text-accent hover:bg-accent-soft"
          >
            <Square size={14} fill="currentColor" aria-hidden="true" />
          </button>
        ) : (
          <button
            type="submit"
            disabled={limited}
            aria-label={chat.send}
            title={chat.send}
            className="flex size-[46px] shrink-0 items-center justify-center rounded-full bg-accent text-accent-ink hover:brightness-108 disabled:bg-subtle disabled:text-muted disabled:hover:brightness-100"
          >
            <ArrowUp size={20} aria-hidden="true" />
          </button>
        )}
      </form>
      <div className="mt-2 hidden flex-wrap items-center gap-x-2 gap-y-1 md:flex">
        <ActionButton
          icon={FileText}
          label={chat.analyseOffer}
          onClick={() => onSend(questions.offer)}
          disabled={busy || limited}
        />
        <ActionButton
          icon={Mail}
          label={chat.contactHim}
          onClick={() => onSend(questions.contact)}
          disabled={busy || limited}
        />
        <span className="ml-auto text-label text-muted">{chat.onlyCv}</span>
      </div>
    </div>
  );
}

type ActionButtonProps = {
  icon: typeof FileText;
  label: string;
  onClick: () => void;
  disabled: boolean;
};

function ActionButton({ icon: Icon, label, onClick, disabled }: ActionButtonProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      className="flex h-9 items-center gap-1.5 rounded-chip px-2.5 text-small font-semibold text-muted hover:bg-subtle disabled:opacity-60 disabled:hover:bg-transparent"
    >
      <Icon size={16} aria-hidden="true" className="text-accent" />
      {label}
    </button>
  );
}
