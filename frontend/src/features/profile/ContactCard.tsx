import { Mail, MessageCircle } from 'lucide-react';
import { useId } from 'react';
import { Card } from '../../components/ui/Card';
import { ExternalLink } from '../../components/ui/ExternalLink';
import { whatsappUrl } from '../../config';
import { useI18n } from '../../i18n/useI18n';
import { profile } from './profile';

const outlined =
  'flex h-10 items-center justify-center gap-2 rounded-full border font-semibold transition-colors duration-(--duration-fast)';

export function ContactCard({ onAsk }: { onAsk: (question: string) => void }) {
  const { messages } = useI18n();
  const titleId = useId();
  const whatsapp = whatsappUrl();
  const { links } = profile.basics;
  return (
    <Card aria-labelledby={titleId} className="flex flex-col gap-2 p-4">
      <h2 id={titleId} className="mb-1 text-heading font-semibold">
        {messages.profile.contact}
      </h2>
      {whatsapp && (
        <ExternalLink
          href={whatsapp}
          className={`${outlined} border-accent text-accent hover:bg-accent-soft`}
        >
          <MessageCircle size={18} aria-hidden="true" />
          {messages.profile.whatsapp}
        </ExternalLink>
      )}
      <div className="flex gap-2">
        <ExternalLink
          href={links.linkedin}
          className={`${outlined} flex-1 border-border-strong text-text hover:bg-subtle`}
        >
          {messages.profile.linkedin}
        </ExternalLink>
        <ExternalLink
          href={links.github}
          className={`${outlined} flex-1 border-border-strong text-text hover:bg-subtle`}
        >
          {messages.profile.github}
        </ExternalLink>
      </div>
      <button
        type="button"
        onClick={() => onAsk(messages.questions.contact)}
        className={`${outlined} border-transparent text-muted hover:bg-subtle`}
      >
        <Mail size={18} aria-hidden="true" />
        {messages.profile.leaveMessage}
      </button>
    </Card>
  );
}
