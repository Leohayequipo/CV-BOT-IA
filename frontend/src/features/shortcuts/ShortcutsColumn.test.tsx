import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import { recentRoles } from '../profile/profile';
import { ShortcutsColumn } from './ShortcutsColumn';

describe('ShortcutsColumn', () => {
  it('asks the question behind each starter', async () => {
    const user = userEvent.setup();
    const onAsk = vi.fn<(question: string) => void>();
    render(<ShortcutsColumn onAsk={onAsk} />);

    await user.click(screen.getByRole('button', { name: /His SaaS in production/ }));

    expect(onAsk).toHaveBeenCalledWith('What is ServiME?');
  });

  it('shows his four latest roles, newest first', () => {
    render(<ShortcutsColumn onAsk={vi.fn<(question: string) => void>()} />);

    const rows = within(screen.getByRole('list')).getAllByRole('listitem');
    expect(rows.map((row) => row.textContent)).toEqual(
      recentRoles(4).map((role) => expect.stringContaining(role.company)),
    );
  });
});
