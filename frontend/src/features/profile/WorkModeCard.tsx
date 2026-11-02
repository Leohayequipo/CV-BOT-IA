import { useId } from 'react';
import { Card } from '../../components/ui/Card';
import { locale, messages } from '../../i18n';
import { localize, profile } from './profile';

export function WorkModeCard() {
  const titleId = useId();
  const languages = profile.languages
    .map((language) => `${localize(language.name, locale)}: ${localize(language.level, locale)}`)
    .join(' · ');
  return (
    <Card aria-labelledby={titleId} className="p-4">
      <h2 id={titleId} className="mb-2 text-heading font-semibold">
        {messages.profile.workMode}
      </h2>
      <p>{localize(profile.basics.work_preference, locale)}.</p>
      <p className="mt-1.5 text-small text-muted">{languages}</p>
    </Card>
  );
}
