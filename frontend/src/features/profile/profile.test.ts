import { describe, expect, it } from 'vitest';
import { localize, recentRoles } from './profile';

describe('recentRoles', () => {
  it('puts the newest role first, whatever the order of the profile', () => {
    const starts = recentRoles(Infinity).map((role) => role.start);

    expect(starts).toEqual(starts.toSorted().toReversed());
  });

  it('returns as many roles as asked', () => {
    expect(recentRoles(2)).toHaveLength(2);
  });
});

describe('localize', () => {
  it('picks the language of the interface', () => {
    expect(localize({ en: 'queues', es: 'colas' }, 'es')).toBe('colas');
  });

  it('keeps a text that reads the same in both languages', () => {
    expect(localize('Python', 'es')).toBe('Python');
  });
});
