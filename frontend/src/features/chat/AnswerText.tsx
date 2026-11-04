import { type ReactNode, useMemo } from 'react';
import { useI18n } from '../../i18n/useI18n';
import { type Block, type Inline, parseInline, parseMarkdown } from '../../lib/markdown';
import type { Citation } from './api';

type AnswerTextProps = {
  text: string;
  citations: Citation[];
  // Drawn after the last word, such as the streaming caret
  trailing?: ReactNode;
};

/** An answer's Markdown as React elements, with a badge for each citation it received. */
export function AnswerText({ text, citations, trailing }: AnswerTextProps) {
  const blocks = useMemo(() => parseMarkdown(text), [text]);
  const sources = new Map(citations.map((citation) => [citation.id, citation]));
  const renderInline = (nodes: Inline[]) =>
    nodes.map((node, index) => renderNode(node, index, sources));

  return (
    <div className="mt-0.5 flex flex-col gap-2 text-answer">
      {blocks.map((block, index) => {
        const tail = index === blocks.length - 1 ? trailing : null;
        return <BlockView key={index} block={block} renderInline={renderInline} tail={tail} />;
      })}
      {blocks.length === 0 && trailing}
    </div>
  );
}

/** One line of Markdown inside a card, such as a job-fit row's evidence, with its badges. */
export function InlineText({ text, citations }: { text: string; citations: Citation[] }) {
  const sources = new Map(citations.map((citation) => [citation.id, citation]));
  return parseInline(text).map((node, index) => renderNode(node, index, sources));
}

type BlockViewProps = {
  block: Block;
  renderInline: (nodes: Inline[]) => ReactNode[];
  tail: ReactNode;
};

function BlockView({ block, renderInline, tail }: BlockViewProps) {
  if (block.type === 'paragraph') {
    return (
      <p className="whitespace-pre-line">
        {renderInline(block.content)}
        {tail}
      </p>
    );
  }
  const List = block.ordered ? 'ol' : 'ul';
  return (
    <List className={`flex flex-col gap-1 pl-5 ${block.ordered ? 'list-decimal' : 'list-disc'}`}>
      {block.items.map((item, index) => (
        <li key={index}>
          {renderInline(item)}
          {index === block.items.length - 1 && tail}
        </li>
      ))}
    </List>
  );
}

function renderNode(node: Inline, key: number, sources: Map<number, Citation>): ReactNode {
  const children = (nodes: Inline[]) =>
    nodes.map((child, index) => renderNode(child, index, sources));
  switch (node.type) {
    case 'text':
      return node.text;
    case 'strong':
      return (
        <strong key={key} className="font-semibold">
          {children(node.children)}
        </strong>
      );
    case 'em':
      return <em key={key}>{children(node.children)}</em>;
    case 'code':
      return (
        <code key={key} className="rounded-badge bg-subtle px-1 font-mono text-[0.9em]">
          {node.text}
        </code>
      );
    case 'link':
      return (
        <a
          key={key}
          href={node.href}
          target="_blank"
          rel="noopener noreferrer"
          className="text-accent underline hover:text-text"
        >
          {children(node.children)}
        </a>
      );
    case 'citation': {
      const source = sources.get(node.id);
      // The contract: a marker with no matching citation stays plain text
      return source ? <CitationBadge key={key} citation={source} /> : `[${node.id}]`;
    }
  }
}

export function CitationBadge({ citation }: { citation: Citation }) {
  const { messages } = useI18n();
  return (
    <span
      title={citation.label}
      className="mx-px inline-block min-w-[18px] rounded-badge bg-accent-soft px-1 text-center align-[1px] text-[11px] leading-[18px] font-bold text-accent"
    >
      <span aria-hidden="true">{citation.id}</span>
      {/* Read as "Source 1: UTN · AI R&D Developer" (DESIGN.md) */}
      <span className="sr-only">
        {messages.chat.source} {citation.id}: {citation.label}
      </span>
    </span>
  );
}

/** Under a finished answer: every source it cited. */
export function SourcesRow({ citations }: { citations: Citation[] }) {
  const { messages } = useI18n();
  if (citations.length === 0) return null;
  return (
    <div className="mt-2.5 flex flex-wrap items-center gap-1.5">
      <span aria-hidden="true" className="mr-0.5 text-label font-semibold text-muted">
        {messages.chat.sources}
      </span>
      <ul aria-label={messages.chat.sources} className="contents">
        {citations.map((citation) => (
          <li
            key={citation.id}
            className="inline-flex items-center gap-1.5 rounded-chip border border-border py-[3px] pr-2 pl-1 text-label"
          >
            <span
              aria-hidden="true"
              className="min-w-4 rounded-[3px] bg-accent-soft px-[3px] text-center text-[11px] leading-4 font-bold text-accent"
            >
              {citation.id}
            </span>
            {citation.label}
          </li>
        ))}
      </ul>
    </div>
  );
}
