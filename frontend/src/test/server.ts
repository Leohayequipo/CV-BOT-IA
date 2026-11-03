/**
 * A fake API for component tests (Mock Service Worker): it streams Server-Sent Events as
 * docs/API.md defines them, so the chat runs its real fetch and stream parsing.
 */
import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';
import { apiUrl } from '../config';

export type ApiEvent = [name: string, payload: unknown];

export const CHAT_URL = `${apiUrl()}/chat`;
export const CONTACT_URL = `${apiUrl()}/contact`;

/** A response that sends each event, in order, as one SSE block. */
export function sse(events: ApiEvent[]): HttpResponse<ReadableStream<Uint8Array>> {
  const encoder = new TextEncoder();
  const body = new ReadableStream<Uint8Array>({
    start(controller) {
      for (const [name, payload] of events) {
        controller.enqueue(encoder.encode(`event: ${name}\ndata: ${JSON.stringify(payload)}\n\n`));
      }
      controller.close();
    },
  });
  return new HttpResponse(body, { headers: { 'Content-Type': 'text/event-stream' } });
}

/** A short complete answer, for tests that only need the chat to work. */
export const answer: ApiEvent[] = [
  ['node', { node: 'profile' }],
  ['token', { text: 'Leonardo builds ' }],
  ['token', { text: 'AI products.' }],
  ['done', { suggestions: ['What is ServiME?'] }],
];

export const server = setupServer(
  http.post(CHAT_URL, () => sse(answer)),
  http.post(CONTACT_URL, () =>
    HttpResponse.json({ sent_at: '2026-11-03T10:32:00Z' }, { status: 202 }),
  ),
);
