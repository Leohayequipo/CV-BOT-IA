/**
 * The page's title, description, sharing tags and structured data, written into index.html
 * when Vite builds or serves it (roadmap step 4.10).
 *
 * Link previews (LinkedIn, WhatsApp, Slack) read only the HTML the server sends, not what React
 * renders, so these tags must be in the file. They come from the profile, so they can't
 * disagree with it.
 */
import type { Plugin } from 'vite';
import profile from '../src/content/profile.json' with { type: 'json' };

type Profile = typeof profile;

const OG_IMAGE = { path: '/og-image.png', width: 1200, height: 630 };

/** The tags for <head>. Without the site's address, the links that must be absolute are left out. */
export function headTags(data: Profile, siteUrl?: string): string {
  const site = siteUrl?.trim().replace(/\/$/, '') || null;
  const { name, headline, links } = data.basics;
  const title = `${name} · ${headline.en}`;
  const description =
    `${headline.en}. Ask his AI assistant about his experience, projects and stack: ` +
    'every answer cites his CV.';
  const image = `${site ?? ''}${OG_IMAGE.path}`;
  const person = {
    '@context': 'https://schema.org',
    '@type': 'Person',
    name,
    jobTitle: headline.en,
    description: data.summary.en.split('\n')[0],
    sameAs: [links.linkedin, links.github],
    knowsLanguage: ['es', 'en'],
    ...(site && { url: `${site}/` }),
  };

  const tags = [
    `<title>${escape(title)}</title>`,
    meta('name', 'description', description),
    site && `<link rel="canonical" href="${escape(`${site}/`)}" />`,
    meta('property', 'og:type', 'profile'),
    meta('property', 'og:title', title),
    meta('property', 'og:description', description),
    site && meta('property', 'og:url', `${site}/`),
    meta('property', 'og:image', image),
    meta('property', 'og:image:width', String(OG_IMAGE.width)),
    meta('property', 'og:image:height', String(OG_IMAGE.height)),
    meta('property', 'og:image:alt', `${name}, ${headline.en}`),
    meta('property', 'og:locale', 'en_US'),
    meta('property', 'og:locale:alternate', 'es_AR'),
    meta('name', 'twitter:card', 'summary_large_image'),
    // The browser's own colours follow the page background in each theme
    '<meta name="theme-color" content="#f2f4f3" media="(prefers-color-scheme: light)" />',
    '<meta name="theme-color" content="#101415" media="(prefers-color-scheme: dark)" />',
    '<link rel="icon" href="/favicon.svg" type="image/svg+xml" />',
    '<link rel="apple-touch-icon" href="/apple-touch-icon.png" />',
    // "<" can't appear in JSON-LD as written, so a value can't close the script tag
    `<script type="application/ld+json">${JSON.stringify(person).replace(/</g, '\\u003c')}</script>`,
  ];
  return tags.filter(Boolean).join('\n    ');
}

/** Replaces the <!-- seo --> marker in index.html with the tags. */
export function seo(siteUrl?: string): Plugin {
  return {
    name: 'cv-seo',
    transformIndexHtml(html) {
      return html.replace('<!-- seo -->', headTags(profile, siteUrl));
    },
  };
}

function meta(attribute: 'name' | 'property', key: string, content: string): string {
  return `<meta ${attribute}="${key}" content="${escape(content)}" />`;
}

function escape(text: string): string {
  return text
    .replace(/&/g, '&amp;')
    .replace(/"/g, '&quot;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}
