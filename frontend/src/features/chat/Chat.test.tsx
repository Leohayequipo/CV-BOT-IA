import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { http, HttpResponse } from 'msw';
import { describe, expect, it } from 'vitest';
import { App } from '../../app/App';
import { answer, CHAT_URL, server, sse } from '../../test/server';

/** The whole chat against the fake API: real fetch, real stream parsing, real reducer. */

function chat() {
  return screen.getByRole('region', { name: "Chat with Leonardo's assistant" });
}

async function ask(question: string) {
  const user = userEvent.setup();
  await user.type(
    within(chat()).getByRole('textbox', { name: 'Your question' }),
    `${question}{Enter}`,
  );
  return user;
}

describe('Chat', () => {
  it('streams the answer to a question and offers the next ones', async () => {
    render(<App />);

    await ask('What does he build?');

    expect(within(chat()).getByText('What does he build?')).toBeInTheDocument();
    expect(await within(chat()).findByText('Leonardo builds AI products.')).toBeInTheDocument();
    expect(
      within(chat()).getAllByRole('button', { name: 'What is ServiME?' }).length,
    ).toBeGreaterThan(0);
  });

  it('sends the earlier messages as history, in the interface language', async () => {
    const bodies: unknown[] = [];
    server.use(
      http.post(CHAT_URL, async ({ request }) => {
        bodies.push(await request.json());
        return sse(answer);
      }),
    );
    render(<App />);

    await ask('First question');
    await within(chat()).findByText('Leonardo builds AI products.');
    await ask('Second question');
    await within(chat()).findAllByText('Leonardo builds AI products.');

    expect(bodies.at(-1)).toMatchObject({
      message: 'Second question',
      locale: 'en',
      history: expect.arrayContaining([
        { role: 'user', content: 'First question' },
        { role: 'assistant', content: 'Leonardo builds AI products.' },
      ]),
    });
  });

  it('shows the typing dots until the first word, and stops on request', async () => {
    // An answer that never arrives
    server.use(
      http.post(
        CHAT_URL,
        () =>
          new HttpResponse(new ReadableStream(), {
            headers: { 'Content-Type': 'text/event-stream' },
          }),
      ),
    );
    render(<App />);

    const user = await ask('Has he led teams?');

    expect(await within(chat()).findByRole('status', { name: 'Typing' })).toBeInTheDocument();
    await user.click(within(chat()).getByRole('button', { name: 'Stop answer' }));
    expect(within(chat()).getByText('You stopped this answer.')).toBeInTheDocument();
    expect(within(chat()).getByRole('button', { name: 'Send question' })).toBeInTheDocument();
  });

  it('shows the error notice when the connection fails, and Retry asks again', async () => {
    server.use(http.post(CHAT_URL, () => HttpResponse.error(), { once: true }));
    render(<App />);

    const user = await ask('Has he led teams?');
    const notice = await within(chat()).findByRole('alert');
    expect(notice).toHaveTextContent("Couldn't connect.");

    await user.click(within(notice).getByRole('button', { name: 'Retry' }));

    expect(await within(chat()).findByText('Leonardo builds AI products.')).toBeInTheDocument();
    expect(within(chat()).queryByRole('alert')).not.toBeInTheDocument();
  });

  it("replaces an answer that fails partway with the API's message", async () => {
    server.use(
      http.post(CHAT_URL, () =>
        sse([
          ['token', { text: 'Leonardo ' }],
          [
            'error',
            {
              code: 'upstream_unavailable',
              message: "The assistant couldn't answer right now. Try again in a moment.",
              retry_after: null,
            },
          ],
        ]),
      ),
    );
    render(<App />);

    await ask('Has he led teams?');

    const notice = await within(chat()).findByRole('alert');
    expect(
      within(notice).getByText("The assistant couldn't answer right now."),
    ).toBeInTheDocument();
    expect(within(notice).getByText('Try again in a moment.')).toBeInTheDocument();
  });

  it('disables the question box while the question limit applies', async () => {
    server.use(
      http.post(CHAT_URL, () =>
        HttpResponse.json(
          {
            error: { code: 'rate_limited', message: "You've reached the question limit for now." },
          },
          { status: 429, headers: { 'Retry-After': '60' } },
        ),
      ),
    );
    render(<App />);

    await ask('Has he led teams?');

    expect(await within(chat()).findByRole('status')).toHaveTextContent('question limit');
    expect(within(chat()).getByRole('textbox', { name: 'Your question' })).toBeDisabled();
  });
});
