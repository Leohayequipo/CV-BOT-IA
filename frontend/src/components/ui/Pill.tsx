import type { ReactNode } from 'react';

/** A technology or skill inside a card. */
export function Pill({ children }: { children: ReactNode }) {
  return (
    <li className="rounded-full border border-border bg-subtle px-2 py-0.5 text-label">
      {children}
    </li>
  );
}
