/**
 * The Markdown the assistant writes (ADR-024): paragraphs, lists, bold, italics, inline code,
 * links and [n] citation markers. It returns a tree, never HTML, so an answer can't inject
 * markup; links are kept only for http and https.
 *
 * Text that is still streaming parses too: an unclosed "**" shows as written until it closes.
 */

export type Inline =
  | { type: 'text'; text: string }
  | { type: 'strong'; children: Inline[] }
  | { type: 'em'; children: Inline[] }
  | { type: 'code'; text: string }
  | { type: 'link'; href: string; children: Inline[] }
  | { type: 'citation'; id: number };

export type Block =
  { type: 'paragraph'; content: Inline[] } | { type: 'list'; ordered: boolean; items: Inline[][] };

const BULLET = /^\s*[-*]\s+(.*)$/;
const NUMBERED = /^\s*\d+[.)]\s+(.*)$/;
const HEADING = /^#{1,6}\s+(.*)$/;
// An indented line continues the list item above it
const CONTINUATION = /^\s{2,}(\S.*)$/;

export function parseMarkdown(text: string): Block[] {
  const blocks: Block[] = [];
  let paragraph: string[] = [];
  // Typed with `as`, so TypeScript doesn't assume it stays null: flush() resets it
  let list = null as { ordered: boolean; items: string[] } | null;

  const flush = () => {
    if (paragraph.length > 0) {
      blocks.push({ type: 'paragraph', content: parseInline(paragraph.join('\n')) });
      paragraph = [];
    }
    if (list) {
      blocks.push({ type: 'list', ordered: list.ordered, items: list.items.map(parseInline) });
      list = null;
    }
  };

  for (const line of text.split('\n')) {
    const bullet = BULLET.exec(line);
    const numbered = NUMBERED.exec(line);
    const item = bullet ?? numbered;
    if (item) {
      const ordered = numbered !== null;
      if (paragraph.length > 0 || list?.ordered !== ordered) flush();
      list ??= { ordered, items: [] };
      list.items.push(item[1] ?? '');
      continue;
    }
    const continuation = CONTINUATION.exec(line);
    if (list && continuation) {
      list.items[list.items.length - 1] += ` ${continuation[1] ?? ''}`;
      continue;
    }
    if (line.trim() === '') {
      flush();
      continue;
    }
    if (list) flush();
    const heading = HEADING.exec(line);
    // Answers have no headings in the design: a heading reads as a bold line
    paragraph.push(heading ? `**${heading[1] ?? ''}**` : line);
  }
  flush();
  return blocks;
}

// In priority order: code, link, citation, bold, then italics with * or _. Underscores inside
// words (snake_case) don't start italics.
const INLINE =
  /`([^`]+)`|\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)|\[(\d+)\]|\*\*(.+?)\*\*|\*([^*\s][^*]*?)\*|(?<!\w)_([^_\s][^_]*?)_(?!\w)/g;

export function parseInline(text: string): Inline[] {
  const nodes: Inline[] = [];
  let last = 0;
  for (const match of text.matchAll(INLINE)) {
    if (match.index > last) nodes.push({ type: 'text', text: text.slice(last, match.index) });
    last = match.index + match[0].length;
    const [, code, label, href, citation, strong, star, underscore] = match;
    if (code !== undefined) nodes.push({ type: 'code', text: code });
    else if (label !== undefined && href !== undefined)
      nodes.push({ type: 'link', href, children: parseInline(label) });
    else if (citation !== undefined) nodes.push({ type: 'citation', id: Number(citation) });
    else if (strong !== undefined) nodes.push({ type: 'strong', children: parseInline(strong) });
    else nodes.push({ type: 'em', children: parseInline(star ?? underscore ?? '') });
  }
  if (last < text.length) nodes.push({ type: 'text', text: text.slice(last) });
  return nodes;
}
