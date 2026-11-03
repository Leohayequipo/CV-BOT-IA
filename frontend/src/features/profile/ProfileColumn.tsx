import { messages } from '../../i18n';
import { ContactCard } from './ContactCard';
import { ProfileCard } from './ProfileCard';
import { WorkModeCard } from './WorkModeCard';

/** The left column on desktop; on a phone, PhoneHeader takes its place. */
export function ProfileColumn({ onAsk }: { onAsk: (question: string) => void }) {
  return (
    <aside
      aria-label={messages.profile.label}
      className="hidden min-w-0 flex-[1_1_260px] flex-col gap-3 md:flex"
    >
      <ProfileCard />
      <ContactCard onAsk={onAsk} />
      <WorkModeCard />
    </aside>
  );
}
