import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { http } from 'msw';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { App } from '../app/App';
import { answer, CHAT_URL, server, sse } from '../test/server';
import { pickLocale } from './index';

function chat(name: RegExp) {
  return screen.getByRole('region', { name });
}

describe('pickLocale', () => {
  it('follows the first language of the browser that the site speaks', () => {
    expect(pickLocale(['es-AR', 'en-US'])).toBe('es');
    expect(pickLocale(['fr-FR', 'en-GB', 'es'])).toBe('en');
  });

  it('falls back to English', () => {
    expect(pickLocale(['fr-FR', 'de'])).toBe('en');
    expect(pickLocale([])).toBe('en');
  });
});

describe('the interface language', () => {
  afterEach(() => {
    vi.restoreAllMocks();
    document.documentElement.lang = 'en';
  });

  it('starts in Spanish when the browser prefers it', () => {
    vi.spyOn(navigator, 'languages', 'get').mockReturnValue(['es-AR', 'es']);

    render(<App />);

    expect(
      within(chat(/asistente de Leonardo/)).getByText(/^Hola, soy el asistente/),
    ).toBeInTheDocument();
    expect(document.documentElement.lang).toBe('es');
  });

  it('switches the whole page, greeting included, and remembers the choice', async () => {
    const user = userEvent.setup();
    render(<App />);

    await user.click(screen.getByRole('button', { name: 'Español' }));

    expect(
      within(chat(/asistente de Leonardo/)).getByText(/^Hola, soy el asistente/),
    ).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Español' })).toHaveAttribute('aria-pressed', 'true');
    expect(screen.getAllByText('AI Engineer · Desarrollador Full Stack').length).toBeGreaterThan(0);
    expect(localStorage.getItem('locale')).toBe('es');
  });

  it('asks the assistant in the chosen language', async () => {
    const bodies: unknown[] = [];
    server.use(
      http.post(CHAT_URL, async ({ request }) => {
        bodies.push(await request.json());
        return sse(answer);
      }),
    );
    const user = userEvent.setup();
    render(<App />);
    await user.click(screen.getByRole('button', { name: 'Español' }));

    await user.type(
      screen.getByRole('textbox', { name: 'Tu pregunta' }),
      '¿Lideró equipos?{Enter}',
    );
    await screen.findByText('Leonardo builds AI products.');

    expect(bodies[0]).toMatchObject({ message: '¿Lideró equipos?', locale: 'es' });
  });
});
