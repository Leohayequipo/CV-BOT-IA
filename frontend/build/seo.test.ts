import { describe, expect, it } from 'vitest';
import profile from '../src/content/profile.json' with { type: 'json' };
import { headTags } from './seo.ts';

function parse(tags: string): Document {
  return new DOMParser().parseFromString(`<head>${tags}</head>`, 'text/html');
}

function content(document: Document, selector: string): string | null {
  return document.querySelector(selector)?.getAttribute('content') ?? null;
}

describe('headTags', () => {
  it('names the page and describes it from the profile', () => {
    const head = parse(headTags(profile, 'https://example.com'));

    expect(head.title).toBe(`${profile.basics.name} · ${profile.basics.headline.en}`);
    expect(content(head, 'meta[name="description"]')).toContain(profile.basics.headline.en);
  });

  it('gives link previews an absolute image and address', () => {
    const head = parse(headTags(profile, 'https://example.com/'));

    expect(content(head, 'meta[property="og:image"]')).toBe('https://example.com/og-image.png');
    expect(content(head, 'meta[property="og:url"]')).toBe('https://example.com/');
    expect(head.querySelector('link[rel="canonical"]')?.getAttribute('href')).toBe(
      'https://example.com/',
    );
  });

  it('leaves out the absolute links until the site has an address', () => {
    const head = parse(headTags(profile, undefined));

    expect(head.querySelector('link[rel="canonical"]')).toBeNull();
    expect(head.querySelector('meta[property="og:url"]')).toBeNull();
  });

  it('describes Leonardo for search engines with his public profiles', () => {
    const head = parse(headTags(profile, 'https://example.com'));

    const person: unknown = JSON.parse(
      head.querySelector('script[type="application/ld+json"]')?.textContent ?? '{}',
    );
    expect(person).toMatchObject({
      '@type': 'Person',
      name: profile.basics.name,
      sameAs: [profile.basics.links.linkedin, profile.basics.links.github],
    });
  });

  it('escapes what goes into attributes and the JSON-LD', () => {
    const tricky = {
      ...profile,
      basics: { ...profile.basics, name: 'A "B" <script>alert(1)</script>' },
    };

    const tags = headTags(tricky, 'https://example.com');

    expect(tags).not.toContain('<script>alert');
    expect(parse(tags).title).toContain('A "B" <script>');
  });
});
