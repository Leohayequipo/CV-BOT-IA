/** One event of a Server-Sent Events stream. */
export type ServerSentEvent = { event: string; data: string };

/**
 * Read a `text/event-stream` body while it arrives, as the HTML standard defines the format:
 * https://html.spec.whatwg.org/multipage/server-sent-events.html#event-stream-interpretation
 *
 * `EventSource` can't send a POST, so the chat reads the response body itself. An event can be
 * split across chunks at any byte; comment lines such as the server's keep-alive pings are skipped.
 */
export async function* readEvents(
  body: ReadableStream<Uint8Array>,
): AsyncGenerator<ServerSentEvent> {
  const reader = body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';
  // A chunk that ends in "\r" may continue with "\n": keep it until the next chunk says
  let carriageReturn = false;
  try {
    for (;;) {
      const { value, done } = await reader.read();
      if (done) return;
      let text: string = (carriageReturn ? '\r' : '') + decoder.decode(value, { stream: true });
      carriageReturn = text.endsWith('\r');
      if (carriageReturn) text = text.slice(0, -1);
      buffer += text.replace(/\r\n?/g, '\n');

      let end = buffer.indexOf('\n\n');
      while (end !== -1) {
        const event = parseEvent(buffer.slice(0, end));
        buffer = buffer.slice(end + 2);
        if (event) yield event;
        end = buffer.indexOf('\n\n');
      }
    }
  } finally {
    // Also runs when the caller stops reading early, so the connection doesn't stay open
    await reader.cancel();
  }
}

function parseEvent(block: string): ServerSentEvent | null {
  let event = 'message';
  const data: string[] = [];
  for (const line of block.split('\n')) {
    if (line.startsWith(':')) continue;
    const colon = line.indexOf(':');
    const field = colon === -1 ? line : line.slice(0, colon);
    const value = colon === -1 ? '' : line.slice(colon + 1).replace(/^ /, '');
    if (field === 'event') event = value;
    if (field === 'data') data.push(value);
  }
  // The standard dispatches nothing for a block without data
  return data.length > 0 ? { event, data: data.join('\n') } : null;
}
