import type { ReactNode } from 'react';
import { AssistantAvatar, VisitorAvatar } from '../../components/ui/Avatar';
import { locale, messages } from '../../i18n';
import type { AssistantMessage, ChatMessage } from './chatState';
import { ErrorNotice } from './Notices';

const time = new Intl.DateTimeFormat(locale, { hour: '2-digit', minute: '2-digit' });

type MessageProps = {
  message: ChatMessage;
  // Only the latest answer offers suggestions and a retry
  footer?: ReactNode;
  onRetry?: () => void;
};

/** No bubbles, as in LinkedIn messaging: avatar, name and time, then the text. */
export function Message({ message, footer, onRetry }: MessageProps) {
  const fromAssistant = message.role === 'assistant';
  return (
    <li className="flex gap-2.5 pt-3.5 md:gap-3 md:pt-4">
      {fromAssistant ? <AssistantAvatar size="message" /> : <VisitorAvatar />}
      <div className="min-w-0 flex-1">
        <p className="flex items-baseline gap-1.5 text-small">
          <strong className="font-semibold">
            {fromAssistant ? messages.chat.assistant : messages.chat.visitor}
          </strong>
          <span aria-hidden="true" className="hidden text-muted md:inline">
            ·
          </span>
          <time dateTime={message.sentAt.toISOString()} className="text-label text-muted">
            {time.format(message.sentAt)}
          </time>
        </p>
        {fromAssistant ? (
          <AnswerBody message={message} onRetry={onRetry} />
        ) : (
          <p className="mt-0.5 text-answer whitespace-pre-line">{message.text}</p>
        )}
        {footer}
      </div>
    </li>
  );
}

function AnswerBody({ message, onRetry }: { message: AssistantMessage; onRetry?: () => void }) {
  switch (message.status) {
    case 'thinking':
      return <TypingDots />;
    case 'failed':
      return message.error && onRetry ? (
        <ErrorNotice error={message.error} onRetry={onRetry} />
      ) : null;
    default:
      return (
        <>
          <p className="mt-0.5 text-answer whitespace-pre-line">
            {message.text}
            {message.status === 'streaming' && <Caret />}
          </p>
          {message.status === 'stopped' && (
            <p className="mt-1 text-label text-muted">{messages.chat.stopped}</p>
          )}
        </>
      );
  }
}

function TypingDots() {
  // <output> is a status region: screen readers say "Typing" once, instead of nothing
  return (
    <output aria-label={messages.chat.typing} className="mt-2 flex h-[18px] items-center gap-1">
      {[0, 150, 300].map((delay) => (
        <span
          key={delay}
          className="size-[7px] rounded-full bg-muted animate-typing motion-reduce:animate-none"
          style={{ animationDelay: `${delay}ms` }}
        />
      ))}
    </output>
  );
}

function Caret() {
  return (
    <span
      aria-hidden="true"
      className="ml-0.5 inline-block h-[15px] w-0.5 translate-y-0.5 bg-accent animate-caret motion-reduce:animate-none"
    />
  );
}
