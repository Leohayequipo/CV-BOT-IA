/**
 * Leonardo's profile, from the JSON copy of content/profile.yaml that the backend exports
 * (ADR-023). TypeScript infers its shape from the file, so a renamed key fails the type check.
 */
import data from '../../content/profile.json';
import type { Locale } from '../../i18n';

export const profile = data;

export type Localized = { readonly en: string; readonly es: string };

export function localize(text: Localized | string, locale: Locale): string {
  return typeof text === 'string' ? text : text[locale];
}

export type Role = {
  key: string;
  company: string;
  url: string | null;
  initials: string;
  title: Localized;
  period: Localized;
  start: string;
  workMode: string | null;
  current: boolean;
  inProfileCard: boolean;
};

// Every role of every company, in the profile's order: by relevance, as in his CV
const roles: Role[] = profile.experience.flatMap((entry) =>
  entry.roles.map((role) => ({
    key: `${entry.id}-${role.start}`,
    company: entry.company,
    url: entry.url,
    initials: entry.initials,
    title: role.title,
    period: role.period,
    start: role.start,
    workMode: role.work_mode,
    current: role.end === null,
    inProfileCard: entry.profile_card,
  })),
);

// "Works today at" on the profile card: the current roles the profile chose to show there
export const currentRoles = roles.filter((role) => role.current && role.inProfileCard);

/** The latest roles, newest first. Partial dates ("2017", "2023-10") sort correctly as text. */
export function recentRoles(count: number): Role[] {
  return roles.toSorted((a, b) => b.start.localeCompare(a.start)).slice(0, count);
}
