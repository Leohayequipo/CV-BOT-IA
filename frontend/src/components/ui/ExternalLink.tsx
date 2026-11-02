import type { ComponentProps } from 'react';
import { messages } from '../../i18n';

/** A link that opens in a new tab and tells screen reader users so. */
export function ExternalLink({ children, ...props }: ComponentProps<'a'>) {
  return (
    <a target="_blank" rel="noopener noreferrer" {...props}>
      {children}
      <span className="sr-only"> {messages.site.opensInNewTab}</span>
    </a>
  );
}
