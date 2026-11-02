import {
  Briefcase,
  Code,
  Download,
  LayoutGrid,
  type LucideIcon,
  Mail,
  MessageSquare,
} from 'lucide-react';
import { cvUrl } from '../config';
import { profile } from '../features/profile/profile';
import { ThemeToggle } from '../features/theme/ThemeToggle';
import type { Theme } from '../features/theme/useTheme';
import { messages } from '../i18n';

type TopBarProps = {
  theme: Theme;
  onToggleTheme: () => void;
  onAsk: (question: string) => void;
};

/** The desktop top bar. Each section asks the assistant, since the chat is the page. */
export function TopBar({ theme, onToggleTheme, onAsk }: TopBarProps) {
  const { nav, questions } = messages;
  const cv = cvUrl();
  return (
    <header className="hidden border-b border-border bg-card md:block">
      <div className="mx-auto flex min-h-14 max-w-[1160px] flex-wrap items-center gap-x-4 gap-y-1 px-4">
        <a href="#chat" className="flex items-center gap-2.5 text-text">
          <span
            aria-hidden="true"
            className="flex size-[34px] items-center justify-center rounded-tile bg-accent font-bold tracking-[0.5px] text-accent-ink"
          >
            {messages.site.monogram}
          </span>
          <span className="flex flex-col leading-tight">
            <span className="text-card-title font-semibold">{profile.basics.name}</span>
            <span className="text-label text-muted">{messages.site.subtitle}</span>
          </span>
        </a>
        <nav aria-label={nav.label} className="ml-auto flex max-w-full overflow-x-auto">
          <a href="#chat" aria-current="page" className={navItem(true)}>
            <MessageSquare size={22} aria-hidden="true" />
            {nav.chat}
          </a>
          <NavButton
            icon={Briefcase}
            label={nav.experience}
            onClick={() => onAsk(questions.experience)}
          />
          <NavButton
            icon={LayoutGrid}
            label={nav.projects}
            onClick={() => onAsk(questions.projects)}
          />
          <NavButton icon={Code} label={nav.skills} onClick={() => onAsk(questions.skills)} />
          <NavButton icon={Mail} label={nav.contact} onClick={() => onAsk(questions.contact)} />
        </nav>
        <div className="flex items-center gap-2 border-l border-border py-1.5 pl-3">
          <ThemeToggle theme={theme} onToggle={onToggleTheme} size="md" />
          {cv && (
            <a
              href={cv}
              className="flex h-10 items-center gap-2 rounded-full bg-accent px-4 font-semibold text-accent-ink hover:brightness-108"
            >
              <Download size={18} aria-hidden="true" />
              {messages.site.downloadCv}
            </a>
          )}
        </div>
      </div>
    </header>
  );
}

function NavButton({
  icon: Icon,
  label,
  onClick,
}: {
  icon: LucideIcon;
  label: string;
  onClick: () => void;
}) {
  return (
    <button type="button" onClick={onClick} className={navItem(false)}>
      <Icon size={22} aria-hidden="true" />
      {label}
    </button>
  );
}

function navItem(current: boolean): string {
  const state = current ? 'border-text text-text' : 'border-transparent text-muted hover:text-text';
  return `flex h-14 min-w-[76px] flex-col items-center justify-center gap-0.5 border-b-2 px-2 pt-1 text-label ${state}`;
}
