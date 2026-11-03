import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import { Composer } from './Composer';

function setup(props: { busy?: boolean; limited?: boolean } = {}) {
  const onSend = vi.fn<(question: string) => void>();
  const onStop = vi.fn<() => void>();
  render(<Composer busy={false} limited={false} onSend={onSend} onStop={onStop} {...props} />);
  return {
    user: userEvent.setup(),
    onSend,
    onStop,
    box: screen.getByRole('textbox', { name: 'Your question' }),
  };
}

describe('Composer', () => {
  it('sends with Enter and clears the box', async () => {
    const { user, onSend, box } = setup();

    await user.type(box, 'Has he led teams?{Enter}');

    expect(onSend).toHaveBeenCalledWith('Has he led teams?');
    expect(box).toHaveValue('');
  });

  it('adds a new line with Shift+Enter instead of sending', async () => {
    const { user, onSend, box } = setup();

    await user.type(box, 'Requirements:{Shift>}{Enter}{/Shift}Python');

    expect(onSend).not.toHaveBeenCalled();
    expect(box).toHaveValue('Requirements:\nPython');
  });

  it('sends nothing when the box is empty', async () => {
    const { user, onSend } = setup();

    await user.click(screen.getByRole('button', { name: 'Send question' }));

    expect(onSend).not.toHaveBeenCalled();
  });

  it('turns the send button into a stop button while an answer streams', async () => {
    const { user, onStop } = setup({ busy: true });

    await user.click(screen.getByRole('button', { name: 'Stop answer' }));

    expect(onStop).toHaveBeenCalled();
  });

  it('disables the box while the question limit applies, and says until when', () => {
    const { box } = setup({ limited: true });

    expect(box).toBeDisabled();
    expect(box).toHaveAttribute('placeholder', 'You can ask again in a few minutes');
  });
});
