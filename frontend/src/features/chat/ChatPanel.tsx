import { ArrowDown, RotateCcw } from 'lucide-react';
import { useLayoutEffect, useRef, useState } from 'react';
import { AssistantAvatar } from '../../components/ui/Avatar';
import { messages } from '../../i18n';
import type { ChatMessage } from './chatState';
import { Composer } from './Composer';
import { Message } from './Message';
import { LimitNotice } from './Notices';
import { SuggestedQuestions } from './SuggestedQuestions';

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
};

/** The centre column on desktop and the whole screen on a phone. */
export function ChatPanel(props: ChatPanelProps) {
  const { conversation, busy, limited, onAsk, onRetry, onStop, onReset } = props;
  const { chat } = messages;
  const latest = conversation.at(-1);
  const suggestions =
    latest?.role === 'assistant' && latest.status === 'done' && !limited ? latest.suggestions : [];

  const list = useRef<HTMLOListElement>(null);
  // The conversation follows new text only while the visitor is at its end, so someone
  // reading an earlier answer isn't pulled down
  const following = useRef(true);
  const [awayFromEnd, setAwayFromEnd] = useState(false);

  // After every render, which is every streamed word
  useLayoutEffect(() => {
    const element = list.current;
    if (!element) return;
    // A new question always brings the conversation to its end
    if (latest?.role === 'assistant' && latest.status === 'thinking') following.current = true;
    if (following.current) element.scrollTop = element.scrollHeight;
  });

  function onScroll() {
    const element = list.current;
    if (!element) return;
    following.current =
      element.scrollHeight - element.scrollTop - element.clientHeight <= END_SLACK;
    setAwayFromEnd(!following.current);
  }

  function jumpToEnd() {
    following.current = true;
    setAwayFromEnd(false);
    if (list.current) list.current.scrollTop = list.current.scrollHeight;
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
        <ol
          ref={list}
          onScroll={onScroll}
          className="h-full overflow-y-auto px-3.5 pb-2 md:px-4 md:pb-[18px]"
        >
          {conversation.map((message) => (
            <Message
              key={message.id}
              message={message}
              {...(message === latest && {
                onRetry,
                footer: <SuggestedQuestions questions={suggestions} onAsk={onAsk} layout="wrap" />,
              })}
            />
          ))}
        </ol>
        {awayFromEnd && busy && (
          <button
            type="button"
            onClick={jumpToEnd}
            className="absolute bottom-3 left-1/2 flex h-9 -translate-x-1/2 items-center gap-1.5 rounded-full border border-accent bg-card px-3.5 text-small font-semibold text-accent hover:bg-accent-soft"
          >
            {chat.newMessage}
            <ArrowDown size={16} aria-hidden="true" />
          </button>
        )}
      </div>
      <Announcement latest={latest} />
      <SuggestedQuestions questions={suggestions} onAsk={onAsk} layout="row" />
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
  const text =
    latest?.role === 'assistant' && latest.status === 'done'
      ? `${messages.chat.assistant}: ${latest.text.replace(/\[\d+\]|[*_`#]/g, '')}`
      : '';
  return (
    <p aria-live="polite" className="sr-only">
      {text}
    </p>
  );
}
