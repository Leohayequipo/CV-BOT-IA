import { describe, expect, it } from 'vitest';
import { cvUrl, whatsappUrl } from './config';

describe('whatsappUrl', () => {
  it('keeps only the digits of the number', () => {
    expect(whatsappUrl('+00 (11) 2222-3333')).toBe('https://wa.me/001122223333');
  });

  it('is null when no number is configured', () => {
    expect(whatsappUrl(undefined)).toBeNull();
    expect(whatsappUrl('')).toBeNull();
  });
});

describe('cvUrl', () => {
  it('is null when no address is configured', () => {
    expect(cvUrl('  ')).toBeNull();
  });
});
