import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { ContactCard } from './ContactCard';
import { profile } from './profile';

describe('ContactCard', () => {
  afterEach(() => {
    vi.unstubAllEnvs();
  });

  it('links to WhatsApp when the phone number is configured', () => {
    vi.stubEnv('VITE_CONTACT_PHONE', '+00 11 2222 3333');

    render(<ContactCard onAsk={vi.fn<(question: string) => void>()} />);

    expect(screen.getByRole('link', { name: /WhatsApp/ })).toHaveAttribute(
      'href',
      'https://wa.me/001122223333',
    );
  });

  it('hides WhatsApp without a phone number', () => {
    vi.stubEnv('VITE_CONTACT_PHONE', '');

    render(<ContactCard onAsk={vi.fn<(question: string) => void>()} />);

    expect(screen.queryByRole('link', { name: /WhatsApp/ })).not.toBeInTheDocument();
  });

  it('links to his LinkedIn and GitHub profiles in a new tab', () => {
    render(<ContactCard onAsk={vi.fn<(question: string) => void>()} />);

    const linkedin = screen.getByRole('link', { name: /LinkedIn/ });
    expect(linkedin).toHaveAttribute('href', profile.basics.links.linkedin);
    expect(linkedin).toHaveAttribute('target', '_blank');
    expect(screen.getByRole('link', { name: /GitHub/ })).toHaveAttribute(
      'href',
      profile.basics.links.github,
    );
  });

  it('asks the assistant to take a message', async () => {
    const user = userEvent.setup();
    const onAsk = vi.fn<(question: string) => void>();
    render(<ContactCard onAsk={onAsk} />);

    await user.click(screen.getByRole('button', { name: 'Leave him a message' }));

    expect(onAsk).toHaveBeenCalledWith("I'd like to leave him a message");
  });
});
