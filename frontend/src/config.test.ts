import { describe, expect, it } from 'vitest';
import { apiUrl, cvUrl, whatsappUrl } from './config';

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

describe('apiUrl', () => {
  it('uses the local backend when no address is configured', () => {
    expect(apiUrl(undefined)).toBe('http://localhost:8001');
  });

  it('drops a trailing slash, so paths join cleanly', () => {
    expect(apiUrl('https://api.example.com/')).toBe('https://api.example.com');
  });
});
