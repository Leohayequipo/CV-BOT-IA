import { ChevronRight, Globe, type LucideIcon, Sparkles, Users, Utensils } from 'lucide-react';
import { useId } from 'react';
import { Card } from '../../components/ui/Card';
import { ExternalLink } from '../../components/ui/ExternalLink';
import { InitialsTile } from '../../components/ui/InitialsTile';
import { REPO_URL } from '../../config';
import { locale, messages } from '../../i18n';
import { localize, recentRoles } from '../profile/profile';

const { shortcuts, questions } = messages;
// Keyed by the profile's work_mode values: remote, hybrid, onsite
const workModes: Partial<Record<string, string>> = messages.workModes;

const STARTERS: { icon: LucideIcon; title: string; subtitle: string; question: string }[] = [
  { icon: Sparkles, ...shortcuts.ai, question: questions.ai },
  { icon: Utensils, ...shortcuts.servime, question: questions.servime },
  { icon: Globe, ...shortcuts.eu, question: questions.eu },
  { icon: Users, ...shortcuts.leadership, question: questions.leadership },
];

/** The right column on desktop: questions to start with and his latest roles. */
export function ShortcutsColumn({ onAsk }: { onAsk: (question: string) => void }) {
  const startId = useId();
  const experienceId = useId();
  return (
    <aside
      aria-label={shortcuts.label}
      className="hidden min-w-0 flex-[1_1_280px] flex-col gap-3 md:flex"
    >
      <Card aria-labelledby={startId} className="px-2.5 pt-4 pb-2">
        <h2 id={startId} className="mx-1.5 mb-1.5 text-title font-semibold">
          {shortcuts.start}
        </h2>
        {STARTERS.map(({ icon: Icon, title, subtitle, question }) => (
          <button
            key={question}
            type="button"
            onClick={() => onAsk(question)}
            className="flex w-full items-center gap-3 rounded-tile px-1.5 py-2.5 text-left hover:bg-subtle"
          >
            <span
              aria-hidden="true"
              className="flex size-10 shrink-0 items-center justify-center rounded-tile bg-accent-soft text-accent"
            >
              <Icon size={20} />
            </span>
            <span className="flex min-w-0 flex-1 flex-col">
              <span className="text-card-title font-semibold">{title}</span>
              <span className="text-small text-muted">{subtitle}</span>
            </span>
            <ChevronRight size={18} aria-hidden="true" className="text-muted" />
          </button>
        ))}
      </Card>
      <Card aria-labelledby={experienceId} className="px-4 pt-4 pb-2">
        <h2 id={experienceId} className="mb-1.5 text-title font-semibold">
          {shortcuts.experience}
        </h2>
        <ul>
          {recentRoles(4).map((role) => (
            <li key={role.key} className="flex gap-3 py-2">
              <InitialsTile initials={role.initials} size="md" />
              <div className="min-w-0">
                <p className="font-semibold">{role.company}</p>
                <p className="text-small">{localize(role.title, locale)}</p>
                <p className="text-label text-muted">
                  {localize(role.period, locale)}
                  {role.workMode && ` · ${workModes[role.workMode] ?? role.workMode}`}
                </p>
              </div>
            </li>
          ))}
        </ul>
        <button
          type="button"
          onClick={() => onAsk(questions.experience)}
          className="mt-1 flex h-10 w-full items-center justify-center gap-1.5 rounded-tile font-semibold text-muted hover:bg-subtle"
        >
          {shortcuts.wholeCareer}
          <ChevronRight size={18} aria-hidden="true" />
        </button>
      </Card>
      <p className="mx-2 mt-0.5 text-center text-label text-muted">
        {shortcuts.openSource} ·{' '}
        <ExternalLink href={REPO_URL} className="text-accent hover:text-text">
          {shortcuts.seeHowItsBuilt}
        </ExternalLink>
      </p>
    </aside>
  );
}
