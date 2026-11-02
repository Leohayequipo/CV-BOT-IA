import { useCallback, useState } from 'react';
import { messages } from '../../i18n';

export type ChatMessage = {
  id: number;
  role: 'assistant' | 'visitor';
  text: string;
  sentAt: Date;
};

/**
 * The conversation shown in the chat panel. Shortcuts and links post their question here;
 * the assistant's streamed answers join it in step 4.5.
 */
export function useConversation() {
  const [conversation, setConversation] = useState<ChatMessage[]>(() => [greeting()]);

  const ask = useCallback((question: string) => {
    setConversation((current) => [
      ...current,
      { id: current.length, role: 'visitor', text: question, sentAt: new Date() },
    ]);
  }, []);

  const reset = useCallback(() => setConversation([greeting()]), []);

  return { conversation, ask, reset };
}

function greeting(): ChatMessage {
  return { id: 0, role: 'assistant', text: messages.chat.greeting, sentAt: new Date() };
}
