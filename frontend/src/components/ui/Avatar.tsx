import { User } from 'lucide-react';
import photo from '../../assets/profile-photo.webp';

type PhotoProps = {
  // Empty when a visible name next to the photo already says who it is
  alt: string;
  className: string;
};

/** Leonardo's photo on its own: it stands for him (ADR-018). */
export function Photo({ alt, className }: PhotoProps) {
  return (
    <img
      src={photo}
      alt={alt}
      width={160}
      height={160}
      className={`block shrink-0 rounded-full object-cover ${className}`}
    />
  );
}

const ASSISTANT_SIZES = {
  // Chat header: 44 px photo, 20 px badge with a 10 px star
  header: { photo: 'size-11', badge: 'size-5', star: 10 },
  // Each answer: 32 px, 30 px on a phone
  message: { photo: 'size-[30px] md:size-8', badge: 'size-[15px] md:size-4', star: 8 },
} as const;

/** The photo with a teal badge: it stands for his assistant, not for him (ADR-011). */
export function AssistantAvatar({ size }: { size: keyof typeof ASSISTANT_SIZES }) {
  const sizes = ASSISTANT_SIZES[size];
  return (
    // self-start: in a message row the wrapper would stretch, and the badge would drift down
    <span className="relative shrink-0 self-start">
      <Photo alt="" className={sizes.photo} />
      <span
        aria-hidden="true"
        className={`absolute -right-[3px] -bottom-[3px] flex items-center justify-center rounded-full border-2 border-card bg-accent text-accent-ink ${sizes.badge}`}
      >
        <svg viewBox="0 0 24 24" width={sizes.star} height={sizes.star} fill="currentColor">
          <path d="M12 2l2.4 7.6L22 12l-7.6 2.4L12 22l-2.4-7.6L2 12l7.6-2.4z" />
        </svg>
      </span>
    </span>
  );
}

/** The visitor: a neutral circle with the user icon. */
export function VisitorAvatar() {
  return (
    <span
      aria-hidden="true"
      className="flex size-[30px] shrink-0 items-center justify-center rounded-full border border-border bg-subtle text-muted md:size-8"
    >
      <User size={16} />
    </span>
  );
}
