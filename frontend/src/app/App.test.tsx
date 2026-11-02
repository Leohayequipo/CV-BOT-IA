import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it } from 'vitest';
import { App } from './App';

function chat() {
  return screen.getByRole('region', { name: "Chat with Leonardo's assistant" });
}

describe('App', () => {
  it('opens with the assistant greeting', () => {
    render(<App />);

    expect(within(chat()).getByText(/^Hi, I'm Leonardo's assistant/)).toBeInTheDocument();
  });

  it('posts the question of a shortcut in the conversation', async () => {
    const user = userEvent.setup();
    render(<App />);

    await user.click(screen.getByRole('button', { name: /AI experience/ }));

    expect(within(chat()).getByText('What AI experience does he have?')).toBeInTheDocument();
  });

  it('asks about a section from the top bar', async () => {
    const user = userEvent.setup();
    render(<App />);

    const sections = screen.getByRole('navigation', { name: 'Sections' });
    await user.click(within(sections).getByRole('button', { name: 'Experience' }));

    expect(within(chat()).getByText('Show me his experience')).toBeInTheDocument();
  });

  it('starts a new conversation with only the greeting', async () => {
    const user = userEvent.setup();
    render(<App />);
    await user.click(screen.getByRole('button', { name: /AI experience/ }));

    await user.click(screen.getByRole('button', { name: 'New conversation' }));

    expect(within(chat()).getAllByRole('listitem')).toHaveLength(1);
  });
});
