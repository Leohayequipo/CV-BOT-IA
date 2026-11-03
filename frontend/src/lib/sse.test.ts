import { describe, expect, it } from 'vitest';
import { readEvents, type ServerSentEvent } from './sse';

function streamOf(...chunks: string[]): ReadableStream<Uint8Array> {
  const encoder = new TextEncoder();
  return new ReadableStream({
    start(controller) {
      for (const chunk of chunks) controller.enqueue(encoder.encode(chunk));
      controller.close();
    },
  });
}

async function collect(stream: ReadableStream<Uint8Array>): Promise<ServerSentEvent[]> {
  const events: ServerSentEvent[] = [];
  for await (const event of readEvents(stream)) events.push(event);
  return events;
}

describe('readEvents', () => {
  it('reads each event with its name and data', async () => {
    const events = await collect(
      streamOf('event: node\ndata: {"node":"guardrail"}\n\nevent: token\ndata: {"text":"Hi"}\n\n'),
    );

    expect(events).toEqual([
      { event: 'node', data: '{"node":"guardrail"}' },
      { event: 'token', data: '{"text":"Hi"}' },
    ]);
  });

  it('joins an event split across chunks at any point', async () => {
    const events = await collect(
      streamOf('eve', 'nt: token\nda', 'ta: {"text":"Leo', '"}\n', '\n'),
    );

    expect(events).toEqual([{ event: 'token', data: '{"text":"Leo"}' }]);
  });

  it('accepts CRLF line endings, even when a chunk ends between the CR and the LF', async () => {
    const events = await collect(streamOf('event: done\r\ndata: {}\r', '\n\r\n'));

    expect(events).toEqual([{ event: 'done', data: '{}' }]);
  });

  it('skips keep-alive comments', async () => {
    const events = await collect(streamOf(': ping\n\nevent: done\ndata: {}\n\n'));

    expect(events).toEqual([{ event: 'done', data: '{}' }]);
  });

  it('joins several data lines with a newline', async () => {
    const events = await collect(streamOf('data: first\ndata: second\n\n'));

    expect(events).toEqual([{ event: 'message', data: 'first\nsecond' }]);
  });

  it('drops an event the stream cut off before its blank line', async () => {
    const events = await collect(streamOf('event: done\ndata: {}\n\nevent: token\ndata: {"te'));

    expect(events).toEqual([{ event: 'done', data: '{}' }]);
  });
});
