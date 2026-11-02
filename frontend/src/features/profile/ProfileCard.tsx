import { ExternalLink as ExternalLinkIcon } from 'lucide-react';
import { Photo } from '../../components/ui/Avatar';
import { Card } from '../../components/ui/Card';
import { ExternalLink } from '../../components/ui/ExternalLink';
import { InitialsTile } from '../../components/ui/InitialsTile';
import { locale, messages } from '../../i18n';
import { CoverGraph } from './CoverGraph';
import { EuBadge } from './EuBadge';
import { currentRoles, localize, profile } from './profile';

export function ProfileCard() {
  const { basics } = profile;
  return (
    <Card className="overflow-hidden">
      <CoverGraph />
      <div className="px-4 pb-4">
        <Photo
          alt={localize(basics.photo.alt, locale)}
          className="relative -mt-10 size-20 border-3 border-card"
        />
        <h1 className="mt-2.5 text-name font-semibold">{basics.name}</h1>
        <p className="mt-1">{localize(basics.headline, locale)}</p>
        <p className="mt-0.5 text-small text-muted">{localize(basics.focus, locale)}</p>
        <p className="mt-2 text-small text-muted">
          {localize(basics.location, locale)} · {localize(basics.citizenship, locale)}
        </p>
        <EuBadge label={messages.profile.euBadge} className="mt-2.5 px-2.5 py-1 text-label" />
      </div>
      <div className="flex flex-col gap-2.5 border-t border-border px-4 pt-3 pb-3.5">
        <h2 className="text-label font-semibold text-muted">{messages.profile.worksAt}</h2>
        <ul className="flex flex-col gap-2.5">
          {currentRoles.map((role) => (
            <li key={role.key} className="flex items-center gap-2.5">
              <InitialsTile initials={role.initials} size="sm" />
              {role.url ? (
                <ExternalLink
                  href={role.url}
                  className="inline-flex items-center gap-1.5 font-semibold text-text hover:text-accent"
                >
                  {role.company}
                  <ExternalLinkIcon size={14} aria-hidden="true" className="text-muted" />
                </ExternalLink>
              ) : (
                <span className="font-semibold">{role.company}</span>
              )}
            </li>
          ))}
        </ul>
      </div>
    </Card>
  );
}
