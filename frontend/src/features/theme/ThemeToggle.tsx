import { Moon, Sun } from 'lucide-react';
import { messages } from '../../i18n';
import type { Theme } from './useTheme';

type ThemeToggleProps = {
  theme: Theme;
  onToggle: () => void;
  // 40 px in the top bar, 44 px in the phone header
  size: 'md' | 'lg';
};

export function ThemeToggle({ theme, onToggle, size }: ThemeToggleProps) {
  const label = theme === 'dark' ? messages.theme.toLight : messages.theme.toDark;
  const Icon = theme === 'dark' ? Sun : Moon;
  return (
    <button
      type="button"
      onClick={onToggle}
      aria-label={label}
      title={label}
      className={`flex shrink-0 items-center justify-center rounded-full text-muted hover:bg-subtle ${size === 'md' ? 'size-10' : 'size-11'}`}
    >
      <Icon size={20} aria-hidden="true" />
    </button>
  );
}
