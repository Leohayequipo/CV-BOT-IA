import type { ComponentProps } from 'react';

/** Cards sit inside an answer, under its text: at most 460 px wide (DESIGN.md). */
export function CardFrame({ className = '', ...props }: ComponentProps<'article'>) {
  return (
    <article
      className={`mt-3 max-w-[460px] overflow-hidden rounded-card border border-border bg-card ${className}`}
      {...props}
    />
  );
}
