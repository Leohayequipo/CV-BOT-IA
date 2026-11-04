import { useCallback, useEffect, useReducer, useRef } from 'react';
import { catalogs, type Messages } from '../../i18n';
import { useI18n } from '../../i18n/useI18n';
import { ChatRequestError, type ChatRequest, sendContact, streamChat } from './api';
import type { ContactSummaryData } from './cards/cardData';
import { type ChatMessage, chatReducer, initialChat, isPending } from './chatState';
import { textOf } from './displayText';

// The API's default limit (docs/API.md); older messages are left out
const MAX_HISTORY = 20;
// When a 429 comes without Retry-After
const DEFAULT_RETRY_AFTER = 60;

// One per page load, only for rate limiting: it identifies no one (docs/API.md)
const sessionId = crypto.randomUUID();

/** The conversation, and the actions that stream answers into it. */
export function useChat() {
  const { locale } = useI18n();
  const [state, dispatch] = useReducer(chatReducer, undefined, () => initialChat());
  const request = useRef<AbortController | null>(null);

  const stream = useCallback(
    async (question: string, earlier: ChatMessage[]) => {
      request.current?.abort();
      const controller = new AbortController();
      request.current = controller;
      // The copy of the language the question was asked in
      const copy = catalogs[locale];
      const body: ChatRequest = {
        message: question,
        history: toHistory(earlier, copy),
        locale,
        session_id: sessionId,
      };
      try {
        let finished = false;
        for await (const event of streamChat(body, controller.signal)) {
          dispatch(event);
          finished ||= event.type === 'done' || event.type === 'error';
        }
        // The connection closed before the answer's last event
        if (!finished) dispatch({ type: 'error', error: networkError(copy) });
      } catch (error) {
        // Stopping or starting over already updated the conversation
        if (controller.signal.aborted) return;
        if (error instanceof ChatRequestError && error.error.code === 'rate_limited') {
          const seconds = error.error.retryAfter ?? DEFAULT_RETRY_AFTER;
          dispatch({ type: 'limited', until: new Date(Date.now() + seconds * 1000) });
        } else {
          dispatch({
            type: 'error',
            error: error instanceof ChatRequestError ? error.error : networkError(copy),
          });
        }
      }
    },
    [locale],
  );

  const latest = state.messages.at(-1);
  const busy = isPending(latest);
  // The cover graph lights up only while the assistant thinks, and rests once words arrive
  const graphNode =
    latest?.role === 'assistant' && latest.status === 'thinking' ? state.node : null;
  const limited = state.limitedUntil !== null;

  const ask = useCallback(
    (question: string) => {
      const text = question.trim();
      if (!text || busy || limited) return;
      dispatch({ type: 'send', question: text, at: new Date() });
      void stream(text, state.messages);
    },
    [busy, limited, state.messages, stream],
  );

  const retry = useCallback(() => {
    const question = state.messages.at(-2);
    if (question?.role !== 'visitor' || limited) return;
    dispatch({ type: 'retry', at: new Date() });
    void stream(question.text, state.messages.slice(0, -2));
  }, [limited, state.messages, stream]);

  const stop = useCallback(() => {
    request.current?.abort();
    dispatch({ type: 'stop' });
  }, []);

  const reset = useCallback(() => {
    request.current?.abort();
    dispatch({ type: 'reset', at: new Date() });
  }, []);

  // Errors reach the card that asked, which shows them next to its buttons
  const confirmContact = useCallback(async (id: number, contact: ContactSummaryData) => {
    const at = await sendContact({ ...contact, session_id: sessionId });
    dispatch({ type: 'contact_sent', id, at });
  }, []);

  // Asking works again once the limit's time is up
  useEffect(() => {
    if (state.limitedUntil === null) return;
    const timer = setTimeout(
      () => dispatch({ type: 'unlimited' }),
      state.limitedUntil.getTime() - Date.now(),
    );
    return () => clearTimeout(timer);
  }, [state.limitedUntil]);

  // Leaving the page mid-answer closes the connection
  useEffect(() => () => request.current?.abort(), []);

  return { ...state, busy, limited, graphNode, ask, retry, stop, reset, confirmContact };
}

/** The finished messages before the question, oldest first, as the API expects them. */
function toHistory(earlier: ChatMessage[], messages: Messages): ChatRequest['history'] {
  return earlier
    .filter((message) => message.role === 'visitor' || message.status === 'done')
    .slice(-MAX_HISTORY)
    .map((message) => ({
      role: message.role === 'visitor' ? 'user' : 'assistant',
      content: textOf(message, messages),
    }));
}

function networkError(messages: Messages) {
  return { code: 'network', message: messages.chat.networkError, retryAfter: null };
}
