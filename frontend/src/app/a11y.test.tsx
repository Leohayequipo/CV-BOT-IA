import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { http, HttpResponse } from 'msw';
import { describe, expect, it } from 'vitest';
import { a11yViolations } from '../test/axe';
import { type ApiEvent, CHAT_URL, server, sse } from '../test/server';
import { App } from './App';

/** Every state of the page, checked with axe against WCAG 2.2 AA (roadmap step 4.9). */

function chat() {
  return screen.getByRole('region', { name: "Chat with Leonardo's assistant" });
}

async function ask(question: string) {
  const user = userEvent.setup();
  await user.type(screen.getByRole('textbox', { name: 'Your question' }), `${question}{Enter}`);
  return user;
}

// One answer with every card type, its citations and the sources row
const everything: ApiEvent[] = [
  [
    'citation',
    {
      id: 1,
      label: 'ServiME · Lead Developer',
      source: 'profile.yaml',
      section: 'experience.servime',
    },
  ],
  ['token', { text: 'He leads **ServiME** [1]:\n\n- Laravel and React\n- OpenAI' }],
  [
    'card',
    {
      type: 'project',
      data: {
        name: 'ServiME',
        summary: 'AI digital menu',
        role: 'Lead Developer',
        period: 'Aug 2026 – present',
        highlight: 'In production [1]',
        stack: ['Laravel'],
        url: 'https://servime.net/',
        brand: 'servime',
      },
    },
  ],
  [
    'card',
    {
      type: 'timeline',
      data: {
        items: [
          {
            role: 'Lead Developer',
            company: 'ServiME',
            period: 'Aug 2026 – present',
            initials: 'SM',
          },
        ],
      },
    },
  ],
  [
    'card',
    { type: 'skills', data: { groups: [{ label: 'Backend', items: ['Python (FastAPI)'] }] } },
  ],
  [
    'card',
    {
      type: 'job_fit',
      data: {
        title: 'AI Engineer',
        requirements: [
          { requirement: 'Python', status: 'met', evidence: 'FastAPI [1]' },
          { requirement: 'AWS', status: 'missing', evidence: 'Not in his CV' },
        ],
      },
    },
  ],
  [
    'card',
    {
      type: 'contact_summary',
      data: {
        name: 'Laura Gómez',
        company: 'Example Ltd',
        email: 'laura.gomez@example.com',
        message: 'Hello',
      },
    },
  ],
  ['done', { suggestions: ['What is ServiME?'] }],
];

describe('accessibility (WCAG 2.2 AA)', () => {
  it('passes on first load', async () => {
    render(<App />);

    expect(await a11yViolations()).toEqual([]);
  });

  it('passes with an answer that has citations and every kind of card', async () => {
    server.use(http.post(CHAT_URL, () => sse(everything)));
    render(<App />);

    await ask('Tell me everything');
    await within(chat()).findAllByRole('article');

    expect(await a11yViolations()).toEqual([]);
  });

  it('passes with the message sent', async () => {
    server.use(http.post(CHAT_URL, () => sse(everything)));
    render(<App />);
    const user = await ask('Leave him a message');

    await user.click(await within(chat()).findByRole('button', { name: 'Send message' }));
    await within(chat()).findByRole('heading', { name: 'Message sent' });

    expect(await a11yViolations()).toEqual([]);
  });

  it('passes with the error notice', async () => {
    server.use(http.post(CHAT_URL, () => HttpResponse.error()));
    render(<App />);

    await ask('Has he led teams?');
    await within(chat()).findByRole('alert');

    expect(await a11yViolations()).toEqual([]);
  });

  it('passes with the question limit', async () => {
    server.use(
      http.post(CHAT_URL, () =>
        HttpResponse.json(
          { error: { code: 'rate_limited', message: "You've reached the question limit." } },
          { status: 429, headers: { 'Retry-After': '60' } },
        ),
      ),
    );
    render(<App />);

    await ask('Has he led teams?');
    await within(chat()).findByRole('status');

    expect(await a11yViolations()).toEqual([]);
  });
});

describe('the accessibility check itself', () => {
  it('catches a problem, so a passing page means something', async () => {
    // A button with no name, built outside JSX so the linter doesn't stop it first
    const button = document.createElement('button');
    button.innerHTML = '<svg aria-hidden="true"></svg>';
    document.body.append(button);

    const violations = await a11yViolations();
    button.remove();

    expect(violations.join(' ')).toContain('button-name');
  });
});

describe('keyboard only', () => {
  it('offers, on the first Tab, to skip straight to the question box', async () => {
    const user = userEvent.setup();
    render(<App />);

    await user.tab();
    expect(screen.getByRole('link', { name: 'Skip to the question box' })).toHaveFocus();

    await user.keyboard('{Enter}');
    expect(screen.getByRole('textbox', { name: 'Your question' })).toHaveFocus();
  });

  it('keeps the keyboard in the question box after sending with Enter', async () => {
    render(<App />);

    await ask('Has he led teams?');

    expect(screen.getByRole('textbox', { name: 'Your question' })).toHaveFocus();
  });

  it('moves the keyboard to the question box when a suggested question goes away', async () => {
    const user = userEvent.setup();
    render(<App />);
    const suggestions = within(chat()).getAllByRole('list', { name: 'Suggested questions' })[0];

    await user.click(
      within(suggestions as HTMLElement).getByRole('button', { name: 'What is ServiME?' }),
    );

    expect(screen.getByRole('textbox', { name: 'Your question' })).toHaveFocus();
  });

  it('keeps the keyboard in the question box after stopping an answer', async () => {
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

    await user.click(within(chat()).getByRole('button', { name: 'Stop answer' }));

    expect(screen.getByRole('textbox', { name: 'Your question' })).toHaveFocus();
  });
});
