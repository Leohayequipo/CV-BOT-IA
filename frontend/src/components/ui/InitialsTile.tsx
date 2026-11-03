/** A company's initials in a grey tile, in place of a logo. */
export function InitialsTile({ initials, size }: { initials: string; size: 'sm' | 'md' }) {
  return (
    <span
      aria-hidden="true"
      className={`flex shrink-0 items-center justify-center rounded-chip border border-border bg-subtle font-bold text-muted ${size === 'sm' ? 'size-8 text-[11px]' : 'size-10 text-label'}`}
    >
      {initials}
    </span>
  );
}
