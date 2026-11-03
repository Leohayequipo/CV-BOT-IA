/** The cards an answer can carry, as docs/API.md defines them, and how to read them safely. */

export type ProjectCardData = {
  name: string;
  summary: string;
  role: string;
  period: string;
  highlight: string;
  stack: string[];
  url: string | null;
  brand: string | null;
};
export type TimelineCardData = {
  items: { role: string; company: string; period: string; initials: string }[];
};
export type SkillsCardData = { groups: { label: string; items: string[] }[] };
export type RequirementStatus = 'met' | 'partial' | 'missing';
export type JobFitCardData = {
  title: string;
  requirements: { requirement: string; status: RequirementStatus; evidence: string }[];
};
export type ContactSummaryData = { name: string; company: string; email: string; message: string };

export type Card =
  | { type: 'project'; data: ProjectCardData }
  | { type: 'timeline'; data: TimelineCardData }
  | { type: 'skills'; data: SkillsCardData }
  | { type: 'job_fit'; data: JobFitCardData }
  | { type: 'contact_summary'; data: ContactSummaryData };

/** The card, or null when its type is unknown or its data breaks the contract. */
export function toCard(type: string, data: unknown): Card | null {
  if (!isRecord(data)) return null;
  switch (type) {
    case 'project':
      return isProject(data) ? { type, data } : null;
    case 'timeline':
      return everyItem(data.items, isTimelineItem) ? { type, data: { items: data.items } } : null;
    case 'skills':
      return everyItem(data.groups, isSkillsGroup) ? { type, data: { groups: data.groups } } : null;
    case 'job_fit':
      return typeof data.title === 'string' && everyItem(data.requirements, isRequirement)
        ? { type, data: { title: data.title, requirements: data.requirements } }
        : null;
    case 'contact_summary':
      return hasStrings(data, ['name', 'company', 'email', 'message']) ? { type, data } : null;
    default:
      return null;
  }
}

function isProject(data: Record<string, unknown>): data is ProjectCardData {
  return (
    hasStrings(data, ['name', 'summary', 'role', 'period', 'highlight']) &&
    everyItem(data.stack, isString) &&
    (data.url === null || isWebAddress(data.url)) &&
    isStringOrNull(data.brand)
  );
}

// The card links to it, so only http and https: never javascript: or data:
function isWebAddress(value: unknown): value is string {
  return (
    typeof value === 'string' && URL.canParse(value) && /^https?:$/.test(new URL(value).protocol)
  );
}

function isTimelineItem(value: unknown): value is TimelineCardData['items'][number] {
  return isRecord(value) && hasStrings(value, ['role', 'company', 'period', 'initials']);
}

function isSkillsGroup(value: unknown): value is SkillsCardData['groups'][number] {
  return isRecord(value) && typeof value.label === 'string' && everyItem(value.items, isString);
}

function isRequirement(value: unknown): value is JobFitCardData['requirements'][number] {
  return (
    isRecord(value) &&
    hasStrings(value, ['requirement', 'evidence']) &&
    (value.status === 'met' || value.status === 'partial' || value.status === 'missing')
  );
}

function hasStrings<K extends string>(
  value: Record<string, unknown>,
  keys: K[],
): value is Record<string, unknown> & Record<K, string> {
  return keys.every((key) => typeof value[key] === 'string');
}

function everyItem<T>(value: unknown, check: (item: unknown) => item is T): value is T[] {
  return Array.isArray(value) && value.every(check);
}

function isString(value: unknown): value is string {
  return typeof value === 'string';
}

function isStringOrNull(value: unknown): value is string | null {
  return value === null || typeof value === 'string';
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}
