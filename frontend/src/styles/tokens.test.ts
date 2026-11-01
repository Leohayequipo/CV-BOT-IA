import { describe, expect, it } from 'vitest';
import designDoc from '../../../docs/DESIGN.md?raw';
import tokensCss from './tokens.css?raw';

type ThemeColours = { light: string; dark: string };

// Rows of the colour table: | `--bg` | Page background | `#F2F4F3` | `#101415` |
const DOC_COLOUR_ROW = /^\| `--([\w-]+)` \| [^|]+ \| `(#[0-9a-f]{6})` \| `(#[0-9a-f]{6})` \|$/gim;
// Rows of the contrast table: | `--text` on `--card` | 16.6:1 | 13.6:1 |
const DOC_CONTRAST_ROW = /^\| `--([\w-]+)` on `--([\w-]+)`[^|]* \| ([\d.]+):1 \| ([\d.]+):1 \|$/gm;
const CSS_COLOUR = /--color-([\w-]+): light-dark\((#[0-9a-f]{6}), (#[0-9a-f]{6})\)/gi;

function coloursFrom(text: string, pattern: RegExp): Map<string, ThemeColours> {
  const colours = new Map<string, ThemeColours>();
  for (const [, name = '', light = '', dark = ''] of text.matchAll(pattern)) {
    colours.set(name, { light: light.toLowerCase(), dark: dark.toLowerCase() });
  }
  return colours;
}

const documented = coloursFrom(designDoc, DOC_COLOUR_ROW);
const implemented = coloursFrom(tokensCss, CSS_COLOUR);

const contrastPairs = [...designDoc.matchAll(DOC_CONTRAST_ROW)].map(
  ([, foreground = '', background = '', light = '', dark = '']) => ({
    foreground,
    background,
    documented: { light: Number(light), dark: Number(dark) },
  }),
);

// WCAG 2.2 relative luminance and contrast ratio
function luminance(hex: string): number {
  const [r = 0, g = 0, b = 0] = [1, 3, 5].map((start) => {
    const channel = Number.parseInt(hex.slice(start, start + 2), 16) / 255;
    return channel <= 0.03928 ? channel / 12.92 : ((channel + 0.055) / 1.055) ** 2.4;
  });
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}

function contrast(foreground: string, background: string): number {
  const [lighter, darker] = [luminance(foreground), luminance(background)].toSorted(
    (a, b) => b - a,
  );
  return ((lighter ?? 0) + 0.05) / ((darker ?? 0) + 0.05);
}

function implementedContrast(foreground: string, background: string, theme: 'light' | 'dark') {
  const fg = implemented.get(foreground)?.[theme];
  const bg = implemented.get(background)?.[theme];
  if (!fg || !bg) {
    throw new Error(`tokens.css is missing --color-${fg ? background : foreground}`);
  }
  return contrast(fg, bg);
}

describe('design tokens', () => {
  it('define every colour in DESIGN.md with its light and dark value', () => {
    expect(documented.size).toBeGreaterThan(0);
    expect(implemented).toEqual(documented);
  });

  it('reach the contrast ratios that DESIGN.md documents', () => {
    expect(contrastPairs.length).toBeGreaterThan(0);
    for (const { foreground, background, documented: ratio } of contrastPairs) {
      expect(implementedContrast(foreground, background, 'light')).toBeCloseTo(ratio.light, 1);
      expect(implementedContrast(foreground, background, 'dark')).toBeCloseTo(ratio.dark, 1);
    }
  });

  it('keep text at WCAG AA and control borders at 3:1 in both themes', () => {
    for (const { foreground, background } of contrastPairs) {
      const minimum = foreground === 'border-strong' ? 3 : 4.5;
      expect(implementedContrast(foreground, background, 'light')).toBeGreaterThanOrEqual(minimum);
      expect(implementedContrast(foreground, background, 'dark')).toBeGreaterThanOrEqual(minimum);
    }
  });
});
