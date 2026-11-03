import { RotateCcw } from 'lucide-react';
import { AssistantAvatar } from '../../components/ui/Avatar';
import { messages } from '../../i18n';
import { Message } from './Message';
import type { ChatMessage } from './useConversation';

type ChatPanelProps = {
  conversation: ChatMessage[];
  onReset: () => void;
};

/** The centre column on desktop and the whole screen on a phone. */
export function ChatPanel({ conversation, onReset }: ChatPanelProps) {
  const { chat } = messages;
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
      <ol aria-live="polite" className="flex-1 overflow-y-auto px-3.5 pb-2 md:px-4 md:pb-[18px]">
        {conversation.map((message) => (
          <Message key={message.id} message={message} />
        ))}
      </ol>
    </section>
  );
}
