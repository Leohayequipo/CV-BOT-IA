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

  it('asks the question of a shortcut', async () => {
    const user = userEvent.setup();
    render(<App />);

    const shortcuts = screen.getByRole('complementary', { name: 'Shortcuts' });
    await user.click(within(shortcuts).getByRole('button', { name: /AI experience/ }));

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
    const sections = screen.getByRole('navigation', { name: 'Sections' });
    await user.click(within(sections).getByRole('button', { name: 'Experience' }));

    await user.click(screen.getByRole('button', { name: 'New conversation' }));

    expect(within(chat()).queryByText('Show me his experience')).not.toBeInTheDocument();
    expect(within(chat()).getByText(/^Hi, I'm Leonardo's assistant/)).toBeInTheDocument();
  });
});
