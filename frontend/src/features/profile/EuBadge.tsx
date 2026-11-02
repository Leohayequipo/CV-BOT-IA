import { ShieldCheck } from 'lucide-react';

/** EU citizenship in teal: one of the facts a recruiter should see first (ADR-018). */
export function EuBadge({ label, className = '' }: { label: string; className?: string }) {
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full bg-accent-soft font-semibold text-accent ${className}`}
    >
      <ShieldCheck size={14} aria-hidden="true" />
      {label}
    </span>
  );
}
