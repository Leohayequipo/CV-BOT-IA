import { AssistantAvatar, VisitorAvatar } from '../../components/ui/Avatar';
import { locale, messages } from '../../i18n';
import type { ChatMessage } from './useConversation';

const time = new Intl.DateTimeFormat(locale, { hour: '2-digit', minute: '2-digit' });

/** No bubbles, as in LinkedIn messaging: avatar, name and time, then the text. */
export function Message({ message }: { message: ChatMessage }) {
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
        <p className="mt-0.5 text-answer whitespace-pre-line">{message.text}</p>
      </div>
    </li>
  );
}
