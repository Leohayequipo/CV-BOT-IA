import { useI18n } from '../../i18n/useI18n';
import { ContactCard } from './ContactCard';
import { ProfileCard } from './ProfileCard';
import { WorkModeCard } from './WorkModeCard';

/** The left column on desktop; on a phone, PhoneHeader takes its place. */
type ProfileColumnProps = {
  onAsk: (question: string) => void;
  activeNode: string | null;
};

export function ProfileColumn({ onAsk, activeNode }: ProfileColumnProps) {
  const { messages } = useI18n();
  return (
    <aside
      aria-label={messages.profile.label}
      className="hidden min-w-0 flex-[1_1_260px] flex-col gap-3 md:flex"
    >
      <ProfileCard activeNode={activeNode} />
      <ContactCard onAsk={onAsk} />
      <WorkModeCard />
    </aside>
  );
}
