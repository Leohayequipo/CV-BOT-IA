import type { ComponentProps } from 'react';

/** A white card on the grey page: 1 px border, 10 px radius, no shadow (DESIGN.md). */
export function Card({ className = '', ...props }: ComponentProps<'section'>) {
  return (
    <section className={`rounded-card border border-border bg-card ${className}`} {...props} />
  );
}
