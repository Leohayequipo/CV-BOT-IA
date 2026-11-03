import { describe, expect, it } from 'vitest';
import { parseInline, parseMarkdown } from './markdown';

describe('parseMarkdown', () => {
  it('splits paragraphs at blank lines and keeps single line breaks', () => {
    expect(parseMarkdown('First line\nsecond line\n\nNext paragraph')).toEqual([
      { type: 'paragraph', content: [{ type: 'text', text: 'First line\nsecond line' }] },
      { type: 'paragraph', content: [{ type: 'text', text: 'Next paragraph' }] },
    ]);
  });

  it('reads bullet and numbered lists, with indented lines continuing an item', () => {
    expect(
      parseMarkdown('His roles:\n- Lead developer\n  at ServiME\n- AI R&D\n\n1. First'),
    ).toEqual([
      { type: 'paragraph', content: [{ type: 'text', text: 'His roles:' }] },
      {
        type: 'list',
        ordered: false,
        items: [
          [{ type: 'text', text: 'Lead developer at ServiME' }],
          [{ type: 'text', text: 'AI R&D' }],
        ],
      },
      { type: 'list', ordered: true, items: [[{ type: 'text', text: 'First' }]] },
    ]);
  });

  it('reads a heading as a bold line', () => {
    expect(parseMarkdown('### Projects')).toEqual([
      {
        type: 'paragraph',
        content: [{ type: 'strong', children: [{ type: 'text', text: 'Projects' }] }],
      },
    ]);
  });
});

describe('parseInline', () => {
  it('turns [n] into a citation', () => {
    expect(parseInline('Built with FastAPI [1].')).toEqual([
      { type: 'text', text: 'Built with FastAPI ' },
      { type: 'citation', id: 1 },
      { type: 'text', text: '.' },
    ]);
  });

  it('reads bold, italics and inline code, nested', () => {
    expect(parseInline('**Lead *developer* at ServiME** with `uv`')).toEqual([
      {
        type: 'strong',
        children: [
          { type: 'text', text: 'Lead ' },
          { type: 'em', children: [{ type: 'text', text: 'developer' }] },
          { type: 'text', text: ' at ServiME' },
        ],
      },
      { type: 'text', text: ' with ' },
      { type: 'code', text: 'uv' },
    ]);
  });

  it('keeps http and https links only', () => {
    expect(parseInline('[ServiME](https://servime.net) and [bad](javascript:alert(1))')).toEqual([
      { type: 'link', href: 'https://servime.net', children: [{ type: 'text', text: 'ServiME' }] },
      { type: 'text', text: ' and [bad](javascript:alert(1))' },
    ]);
  });

  it('leaves HTML as plain text', () => {
    expect(parseInline('<img src=x onerror=alert(1)>')).toEqual([
      { type: 'text', text: '<img src=x onerror=alert(1)>' },
    ]);
  });

  it('leaves underscores inside words alone', () => {
    expect(parseInline('the job_fit_card type')).toEqual([
      { type: 'text', text: 'the job_fit_card type' },
    ]);
  });

  it('shows an unclosed marker as written while the answer streams', () => {
    expect(parseInline('He led **a team')).toEqual([{ type: 'text', text: 'He led **a team' }]);
  });
});
