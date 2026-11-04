import { Download, MessageCircle } from 'lucide-react';
import { Photo } from '../../components/ui/Avatar';
import { ExternalLink } from '../../components/ui/ExternalLink';
import { cvUrl, whatsappUrl } from '../../config';
import { useI18n } from '../../i18n/useI18n';
import { ThemeToggle } from '../theme/ThemeToggle';
import type { Theme } from '../theme/useTheme';
import { EuBadge } from './EuBadge';
import { localize, profile } from './profile';

const pill =
  'inline-flex min-h-9 shrink-0 items-center gap-1.5 rounded-full border px-3.5 text-small font-semibold';

type PhoneHeaderProps = {
  theme: Theme;
  onToggleTheme: () => void;
};

/** On a phone the profile collapses into this header, so the chat gets the whole screen. */
export function PhoneHeader({ theme, onToggleTheme }: PhoneHeaderProps) {
  const { messages, locale } = useI18n();
  const { basics } = profile;
  const whatsapp = whatsappUrl();
  const cv = cvUrl();
  return (
    <div className="border-b border-border bg-card md:hidden">
      <header className="flex items-center gap-2.5 py-1.5 pr-1 pl-3.5">
        <Photo alt={localize(basics.photo.alt, locale)} className="size-10" />
        <div className="min-w-0 flex-1">
          <h1 className="text-card-title font-semibold">{basics.name}</h1>
          <p className="truncate text-label text-muted">{localize(basics.headline, locale)}</p>
        </div>
        <ThemeToggle theme={theme} onToggle={onToggleTheme} size="lg" />
        {cv && (
          <a
            href={cv}
            aria-label={messages.site.downloadCv}
            title={messages.site.downloadCv}
            className="flex size-11 shrink-0 items-center justify-center rounded-full text-accent hover:bg-subtle"
          >
            <Download size={20} aria-hidden="true" />
          </a>
        )}
      </header>
      <div className="flex gap-2 overflow-x-auto border-t border-border px-3.5 pt-2 pb-2.5">
        <EuBadge
          label={messages.profile.euBadgeShort}
          className="min-h-9 shrink-0 px-3 text-small"
        />
        {whatsapp && (
          <ExternalLink href={whatsapp} className={`${pill} border-accent text-accent`}>
            <MessageCircle size={16} aria-hidden="true" />
            {messages.profile.whatsapp}
          </ExternalLink>
        )}
        <ExternalLink href={basics.links.linkedin} className={`${pill} border-border-strong`}>
          {messages.profile.linkedin}
        </ExternalLink>
        <ExternalLink href={basics.links.github} className={`${pill} border-border-strong`}>
          {messages.profile.github}
        </ExternalLink>
      </div>
    </div>
  );
}
