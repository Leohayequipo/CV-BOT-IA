/** The client of POST /chat, as docs/API.md defines it. */
import { apiUrl } from '../../config';
import type { Locale } from '../../i18n';
import { readEvents } from '../../lib/sse';

export type Citation = { id: number; label: string; source: string; section: string };
// Step 4.6 gives each card type its own shape
export type Card = { type: string; data: unknown };
export type ChatError = { code: string; message: string; retryAfter: number | null };

export type StreamEvent =
  | { type: 'node'; node: string }
  | { type: 'token'; text: string }
  | { type: 'citation'; citation: Citation }
  | { type: 'card'; card: Card }
  | { type: 'done'; suggestions: string[] }
  | { type: 'error'; error: ChatError };

export type ChatRequest = {
  message: string;
  history: { role: 'user' | 'assistant'; content: string }[];
  locale: Locale;
  session_id: string;
};

/** The API refused the question before streaming: an invalid body, the limit or a failure. */
export class ChatRequestError extends Error {
  readonly error: ChatError;

  constructor(error: ChatError) {
    super(error.message);
    this.name = 'ChatRequestError';
    this.error = error;
  }
}

/** Ask a question and yield the answer's events as they arrive. Aborting the signal stops it. */
export async function* streamChat(
  request: ChatRequest,
  signal: AbortSignal,
): AsyncGenerator<StreamEvent> {
  const response = await fetch(`${apiUrl()}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
    signal,
  });
  if (!response.ok || !response.body) {
    throw new ChatRequestError(await readError(response));
  }
  for await (const { event, data } of readEvents(response.body)) {
    const parsed = toStreamEvent(event, parseJson(data));
    if (parsed) yield parsed;
  }
}

// Unknown or malformed events are skipped, so the API can add events without breaking the site
function toStreamEvent(name: string, payload: unknown): StreamEvent | null {
  if (!isRecord(payload)) return null;
  switch (name) {
    case 'node':
      return typeof payload.node === 'string' ? { type: 'node', node: payload.node } : null;
    case 'token':
      return typeof payload.text === 'string' ? { type: 'token', text: payload.text } : null;
    case 'citation':
      return isCitation(payload) ? { type: 'citation', citation: payload } : null;
    case 'card':
      return typeof payload.type === 'string'
        ? { type: 'card', card: { type: payload.type, data: payload.data } }
        : null;
    case 'done':
      return { type: 'done', suggestions: strings(payload.suggestions) };
    case 'error':
      return { type: 'error', error: toChatError(payload) };
    default:
      return null;
  }
}

async function readError(response: Response): Promise<ChatError> {
  const body: unknown = await response.json().catch(() => null);
  const error = isRecord(body) && isRecord(body.error) ? body.error : {};
  const retryAfter = Number.parseInt(response.headers.get('Retry-After') ?? '', 10);
  return { ...toChatError(error), retryAfter: Number.isNaN(retryAfter) ? null : retryAfter };
}

function toChatError(payload: Record<string, unknown>): ChatError {
  return {
    code: typeof payload.code === 'string' ? payload.code : 'internal_error',
    message: typeof payload.message === 'string' ? payload.message : '',
    retryAfter: typeof payload.retry_after === 'number' ? payload.retry_after : null,
  };
}

function parseJson(text: string): unknown {
  try {
    return JSON.parse(text);
  } catch {
    return null;
  }
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

function isCitation(value: Record<string, unknown>): value is Citation {
  return (
    typeof value.id === 'number' &&
    typeof value.label === 'string' &&
    typeof value.source === 'string' &&
    typeof value.section === 'string'
  );
}

function strings(value: unknown): string[] {
  return Array.isArray(value) ? value.filter((item) => typeof item === 'string') : [];
}
