/**
 * The conversation as a reducer: the stream's events are actions, so the API contract and the
 * state change in one place. Only the latest answer ever changes.
 */
import type { ChatError, Citation, StreamEvent } from './api';
import type { Card } from './cards/cardData';

export type AnswerStatus = 'thinking' | 'streaming' | 'done' | 'stopped' | 'failed';

export type VisitorMessage = { id: number; role: 'visitor'; text: string; sentAt: Date };

// The greeting and the "message sent" reply are written by the site, not the API: their text
// comes from the interface copy when they're drawn, so they follow the language
export type AnswerKind = 'answer' | 'greeting' | 'contact_sent';

export type AssistantMessage = {
  id: number;
  role: 'assistant';
  kind: AnswerKind;
  text: string;
  sentAt: Date;
  status: AnswerStatus;
  citations: Citation[];
  cards: Card[];
  suggestions: string[];
  error: ChatError | null;
  // When the visitor confirmed this answer's contact summary
  confirmedAt: Date | null;
  // Set on the reply that says the message was sent, which shows the message-sent card
  contactSentAt: Date | null;
};

export type ChatMessage = VisitorMessage | AssistantMessage;

export type ChatState = {
  messages: ChatMessage[];
  // The graph step working on the answer, for the cover graph (step 4.7)
  node: string | null;
  // Set while the question limit applies; the question box stays disabled until then
  limitedUntil: Date | null;
};

export type ChatAction =
  | StreamEvent
  | { type: 'send'; question: string; at: Date }
  | { type: 'retry'; at: Date }
  | { type: 'stop' }
  | { type: 'limited'; until: Date }
  | { type: 'unlimited' }
  | { type: 'contact_sent'; id: number; at: Date }
  | { type: 'reset'; at: Date };

export function initialChat(at = new Date()): ChatState {
  const greeting: AssistantMessage = { ...answer(0, at), kind: 'greeting', status: 'done' };
  return { messages: [greeting], node: null, limitedUntil: null };
}

export function chatReducer(state: ChatState, action: ChatAction): ChatState {
  switch (action.type) {
    case 'send': {
      const id = state.messages.length;
      const question: VisitorMessage = {
        id,
        role: 'visitor',
        text: action.question,
        sentAt: action.at,
      };
      return { ...state, messages: [...state.messages, question, answer(id + 1, action.at)] };
    }
    case 'retry':
      // The notice stays, with its icon spinning, until the new answer starts
      return updateAnswer(state, (last) => ({ ...answer(last.id, action.at), error: last.error }));
    case 'node':
      return { ...state, node: action.node };
    case 'token':
      return updateAnswer(state, (last) => ({
        ...last,
        text: last.text + action.text,
        status: 'streaming',
        error: null,
      }));
    case 'citation':
      return updateAnswer(state, (last) =>
        last.citations.some((citation) => citation.id === action.citation.id)
          ? last
          : { ...last, citations: [...last.citations, action.citation] },
      );
    case 'card':
      return updateAnswer(state, (last) => ({ ...last, cards: [...last.cards, action.card] }));
    case 'done':
      return {
        ...updateAnswer(state, (last) => ({
          ...last,
          status: 'done',
          suggestions: action.suggestions,
          error: null,
        })),
        node: null,
      };
    case 'error':
      return {
        ...updateAnswer(state, (last) => ({ ...last, status: 'failed', error: action.error })),
        node: null,
      };
    case 'stop':
      return {
        ...updateAnswer(state, (last) =>
          last.status === 'thinking' || last.status === 'streaming'
            ? { ...last, status: 'stopped' }
            : last,
        ),
        node: null,
      };
    case 'limited':
      // The question wasn't answered: drop the waiting answer and keep the question visible
      return {
        messages: state.messages.filter((message) => !isPending(message)),
        node: null,
        limitedUntil: action.until,
      };
    case 'unlimited':
      return { ...state, limitedUntil: null };
    case 'contact_sent': {
      const conversation = state.messages.map((message) =>
        message.id === action.id && message.role === 'assistant'
          ? { ...message, confirmedAt: action.at }
          : message,
      );
      const reply: AssistantMessage = {
        ...answer(conversation.length, action.at),
        kind: 'contact_sent',
        status: 'done',
        contactSentAt: action.at,
      };
      return { ...state, messages: [...conversation, reply] };
    }
    case 'reset':
      return { ...initialChat(action.at), limitedUntil: state.limitedUntil };
  }
}

/** The latest answer, when it's still waiting for the stream or receiving it. */
export function isPending(message: ChatMessage | undefined): boolean {
  return (
    message?.role === 'assistant' &&
    (message.status === 'thinking' || message.status === 'streaming')
  );
}

function answer(id: number, at: Date): AssistantMessage {
  return {
    id,
    role: 'assistant',
    kind: 'answer',
    text: '',
    sentAt: at,
    status: 'thinking',
    citations: [],
    cards: [],
    suggestions: [],
    error: null,
    confirmedAt: null,
    contactSentAt: null,
  };
}

function updateAnswer(
  state: ChatState,
  update: (last: AssistantMessage) => AssistantMessage,
): ChatState {
  const last = state.messages.at(-1);
  if (last?.role !== 'assistant') return state;
  return { ...state, messages: [...state.messages.slice(0, -1), update(last)] };
}
