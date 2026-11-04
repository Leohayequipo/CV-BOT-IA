import { describe, expect, it } from 'vitest';
import {
  type AssistantMessage,
  type ChatAction,
  type ChatState,
  chatReducer,
  initialChat,
} from './chatState';

const at = new Date('2026-11-03T10:25:00Z');

function run(...actions: ChatAction[]): ChatState {
  return actions.reduce(chatReducer, initialChat(at));
}

function latest(state: ChatState): AssistantMessage {
  const message = state.messages.at(-1);
  if (message?.role !== 'assistant') throw new Error('the latest message is not an answer');
  return message;
}

const send: ChatAction = { type: 'send', question: 'Has he led teams?', at };

describe('chatReducer', () => {
  it('opens with the greeting and its suggested questions', () => {
    const greeting = latest(initialChat(at));

    expect(greeting.status).toBe('done');
    expect(greeting.suggestions.length).toBeGreaterThan(0);
  });

  it('adds the question and an answer that is thinking', () => {
    const state = run(send);

    expect(state.messages.at(-2)).toMatchObject({ role: 'visitor', text: 'Has he led teams?' });
    expect(latest(state).status).toBe('thinking');
  });

  it('streams the words into the latest answer', () => {
    const state = run(send, { type: 'token', text: 'He led ' }, { type: 'token', text: 'a team.' });

    expect(latest(state)).toMatchObject({ text: 'He led a team.', status: 'streaming' });
  });

  it('keeps each citation once', () => {
    const citation = { id: 1, label: 'Profile', source: 'profile.yaml', section: 'summary' };

    const state = run(send, { type: 'citation', citation }, { type: 'citation', citation });

    expect(latest(state).citations).toEqual([citation]);
  });

  it('finishes the answer with its suggestions', () => {
    const state = run(
      send,
      { type: 'token', text: 'Yes.' },
      { type: 'done', suggestions: ['Next?'] },
    );

    expect(latest(state)).toMatchObject({ status: 'done', suggestions: ['Next?'] });
  });

  it('marks a failed answer, and a retry keeps the notice until the new answer starts', () => {
    const error = { code: 'upstream_unavailable', message: 'Failed. Retry.', retryAfter: null };
    const failed = run(send, { type: 'token', text: 'He' }, { type: 'error', error });
    expect(latest(failed)).toMatchObject({ status: 'failed', error });

    const retrying = chatReducer(failed, { type: 'retry', at });
    expect(latest(retrying)).toMatchObject({ status: 'thinking', text: '', error });

    const answering = chatReducer(retrying, { type: 'token', text: 'He led' });
    expect(latest(answering)).toMatchObject({ status: 'streaming', text: 'He led', error: null });
  });

  it('stops only an answer still in progress', () => {
    expect(latest(run(send, { type: 'stop' })).status).toBe('stopped');
    expect(latest(run({ type: 'stop' })).status).toBe('done');
  });

  it('keeps the question but drops the waiting answer when the limit applies', () => {
    const until = new Date('2026-11-03T10:26:00Z');

    const state = run(send, { type: 'limited', until });

    expect(state.messages.at(-1)).toMatchObject({ role: 'visitor', text: 'Has he led teams?' });
    expect(state.limitedUntil).toEqual(until);
  });

  it('starts over with the greeting, but a new conversation keeps the limit', () => {
    const until = new Date('2026-11-03T10:26:00Z');

    const state = run(send, { type: 'limited', until }, { type: 'reset', at });

    expect(state.messages).toHaveLength(1);
    expect(state.limitedUntil).toEqual(until);
  });
});

describe('contact', () => {
  it('marks the summary as confirmed and adds the reply with the message-sent card', () => {
    const sent = new Date('2026-11-03T10:32:00Z');
    const asked = run(send, { type: 'done', suggestions: [] });
    const summaryId = latest(asked).id;

    const state = chatReducer(asked, { type: 'contact_sent', id: summaryId, at: sent });

    expect(state.messages.find((message) => message.id === summaryId)).toMatchObject({
      confirmedAt: sent,
    });
    expect(latest(state)).toMatchObject({ status: 'done', contactSentAt: sent });
  });
});
