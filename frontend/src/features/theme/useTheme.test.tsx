import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, beforeEach, describe, expect, it } from 'vitest';
import { setSystemTheme } from '../../test/setup';
import { ThemeToggle } from './ThemeToggle';
import { useTheme } from './useTheme';

function Toggle() {
  const { theme, toggleTheme } = useTheme();
  return <ThemeToggle theme={theme} onToggle={toggleTheme} size="md" />;
}

describe('useTheme', () => {
  beforeEach(() => setSystemTheme('light'));

  afterEach(() => {
    localStorage.clear();
    delete document.documentElement.dataset.theme;
  });

  it('follows the OS until the visitor chooses', () => {
    setSystemTheme('dark');

    render(<Toggle />);

    expect(screen.getByRole('button', { name: 'Switch to light mode' })).toBeInTheDocument();
    expect(document.documentElement.dataset.theme).toBeUndefined();
  });

  it('applies and remembers the theme the visitor picks', async () => {
    const user = userEvent.setup();
    render(<Toggle />);

    await user.click(screen.getByRole('button', { name: 'Switch to dark mode' }));

    expect(document.documentElement.dataset.theme).toBe('dark');
    expect(localStorage.getItem('theme')).toBe('dark');
    expect(screen.getByRole('button', { name: 'Switch to light mode' })).toBeInTheDocument();
  });

  it('starts from the theme chosen on an earlier visit', () => {
    localStorage.setItem('theme', 'dark');

    render(<Toggle />);

    expect(screen.getByRole('button', { name: 'Switch to light mode' })).toBeInTheDocument();
  });
});
