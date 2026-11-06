import { ArrowDown, RotateCcw } from 'lucide-react';
import { useEffect, useLayoutEffect, useRef, useState } from 'react';
import { AssistantAvatar } from '../../components/ui/Avatar';
import { useI18n } from '../../i18n/useI18n';
import type { ChatMessage } from './chatState';
import { Composer } from './Composer';
import { type ContactHandlers, Message } from './Message';
import { LimitNotice } from './Notices';
import { SuggestedQuestions } from './SuggestedQuestions';
import { suggestionsOf, textOf } from './displayText';
import { focusQuestionBox } from './questionBox';

// How close to the end still counts as "at the end", in pixels
const END_SLACK = 32;

type ChatPanelProps = {
  conversation: ChatMessage[];
  busy: boolean;
  limited: boolean;
  onAsk: (question: string) => void;
  onRetry: () => void;
  onStop: () => void;
  onReset: () => void;
  onSendContact: ContactHandlers['onConfirm'];
};

/** Slides to the end in 320 ms (DESIGN.md); under reduced motion it jumps there. */
function scrollToEnd(element: HTMLElement) {
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  element.scrollTo({ top: element.scrollHeight, behavior: reduce ? 'instant' : 'smooth' });
}

/** The centre column on desktop and the whole screen on a phone. */
export function ChatPanel(props: ChatPanelProps) {
  const { messages } = useI18n();
  const { conversation, busy, limited, onAsk, onRetry, onStop, onReset, onSendContact } = props;
  // A chip or the retry button goes away once used: the keyboard moves to the question box
  const askFromChip = (question: string) => {
    onAsk(question);
    focusQuestionBox();
  };
  const retry = () => {
    onRetry();
    focusQuestionBox();
  };
  const contact: ContactHandlers = {
    onConfirm: onSendContact,
    // The assistant asks again what to change, as the contact agent will (step 6.3)
    onCorrect: () => onAsk(messages.questions.correct),
  };
  const { chat } = messages;
  const latest = conversation.at(-1);
  const suggestions =
    latest?.role === 'assistant' && latest.status === 'done' && !limited
      ? suggestionsOf(latest, messages)
      : [];

  // What's there on the first render appears at once: the page load never animates
  const [initialIds] = useState(() => new Set(conversation.map((message) => message.id)));
  const scroller = useRef<HTMLDivElement>(null);
  const list = useRef<HTMLOListElement>(null);
  // The conversation follows new text only while the visitor is at its end, so someone
  // reading an earlier answer isn't pulled down
  const following = useRef(true);
  const lastTop = useRef(0);
  const [awayFromEnd, setAwayFromEnd] = useState(false);

  // A new question always brings the conversation to its end
  useLayoutEffect(() => {
    if (latest?.role === 'assistant' && latest.status === 'thinking') following.current = true;
  });

  // Follow the conversation as it grows: each streamed word, and cards that load a moment later
  useEffect(() => {
    const element = scroller.current;
    const content = list.current;
    if (!element || !content || typeof ResizeObserver === 'undefined') return;
    const observer = new ResizeObserver(() => {
      if (following.current) scrollToEnd(element);
    });
    observer.observe(content);
    return () => observer.disconnect();
  }, []);

  // Only the visitor scrolls up: the smooth scroll above only goes down, so it can't be
  // mistaken for the visitor leaving the end
  function onScroll() {
    const element = scroller.current;
    if (!element) return;
    const atEnd = element.scrollHeight - element.scrollTop - element.clientHeight <= END_SLACK;
    if (element.scrollTop < lastTop.current - 1) following.current = false;
    if (atEnd) following.current = true;
    lastTop.current = element.scrollTop;
    setAwayFromEnd(!following.current);
  }

  function jumpToEnd() {
    following.current = true;
    setAwayFromEnd(false);
    if (scroller.current) scrollToEnd(scroller.current);
  }

  return (
    <section
      id="chat"
      aria-label={chat.label}
      className="flex min-h-0 min-w-0 flex-1 flex-col overflow-hidden bg-card md:h-[700px] md:flex-[999_1_480px] md:rounded-card md:border md:border-border"
    >
      <div className="hidden items-center gap-3 border-b border-border px-4 py-3 md:flex">
        <AssistantAvatar size="header" />
        <div className="min-w-0 flex-1">
          <h2 className="text-heading font-semibold">{chat.assistant}</h2>
          <p className="mt-0.5 text-label text-muted">{chat.subtitle}</p>
        </div>
        <button
          type="button"
          onClick={onReset}
          aria-label={chat.newConversation}
          title={chat.newConversation}
          className="flex size-10 items-center justify-center rounded-full text-muted hover:bg-subtle"
        >
          <RotateCcw size={20} aria-hidden="true" />
        </button>
      </div>
      <div className="relative min-h-0 flex-1">
        <div
          ref={scroller}
          onScroll={onScroll}
          className="flex h-full flex-col overflow-y-auto px-3.5 pb-2 md:px-4 md:pb-[18px]"
        >
          {/* mt-auto anchors a short conversation to the bottom, next to the question box */}
          <ol ref={list} aria-label={chat.conversation} className="mt-auto">
            {conversation.map((message) => (
              <Message
                key={message.id}
                message={message}
                contact={contact}
                enter={!initialIds.has(message.id)}
                {...(message === latest && {
                  onRetry: retry,
                  footer: (
                    <SuggestedQuestions questions={suggestions} onAsk={askFromChip} layout="wrap" />
                  ),
                })}
              />
            ))}
          </ol>
        </div>
        {awayFromEnd && busy && (
          <button
            type="button"
            onClick={jumpToEnd}
            className="absolute bottom-3 left-1/2 flex h-9 -translate-x-1/2 animate-fade-in items-center gap-1.5 rounded-full border border-accent bg-card px-3.5 text-small font-semibold text-accent hover:bg-accent-soft"
          >
            {chat.newMessage}
            <ArrowDown size={16} aria-hidden="true" />
          </button>
        )}
      </div>
      <Announcement latest={latest} />
      <SuggestedQuestions questions={suggestions} onAsk={askFromChip} layout="row" />
      {limited && <LimitNotice />}
      <Composer busy={busy} limited={limited} onSend={onAsk} onStop={onStop} />
    </section>
  );
}

/**
 * Screen readers hear each answer once it's complete. A live region on the list itself would
 * read every streamed word.
 */
function Announcement({ latest }: { latest: ChatMessage | undefined }) {
  const { messages } = useI18n();
  const text =
    latest?.role === 'assistant' && latest.status === 'done'
      ? `${messages.chat.assistant}: ${textOf(latest, messages).replace(/\[\d+\]|[*_`#]/g, '')}`
      : '';
  return (
    <p aria-live="polite" className="sr-only">
      {text}
    </p>
  );
}
