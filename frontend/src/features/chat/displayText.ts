import type { Messages } from '../../i18n';
import type { ChatMessage } from './chatState';

/** What a message says, in the interface language for the ones the site writes itself. */
export function textOf(message: ChatMessage, messages: Messages): string {
  if (message.role === 'visitor') return message.text;
  switch (message.kind) {
    case 'greeting':
      return messages.chat.greeting;
    case 'contact_sent':
      return messages.chat.contactSent;
    case 'answer':
      return message.text;
  }
}

/** The questions offered after a message. */
export function suggestionsOf(message: ChatMessage, messages: Messages): string[] {
  if (message.role === 'visitor') return [];
  switch (message.kind) {
    case 'greeting':
      return messages.chat.firstSuggestions;
    case 'contact_sent':
      return messages.chat.afterContact;
    case 'answer':
      return message.suggestions;
  }
}
