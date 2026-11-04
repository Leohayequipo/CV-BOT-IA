/**
 * Lower-cases a value's first letter so it can follow other words ("Nativo" → "nativo"),
 * but leaves codes and acronyms alone ("B1", "UE").
 */
export function lowerFirst(text: string): string {
  const [first = '', second = ''] = text;
  return second && second === second.toUpperCase() ? text : first.toLowerCase() + text.slice(1);
}
