import axe from 'axe-core';

/**
 * The WCAG 2.2 A and AA problems axe finds in the rendered page, one line each, so a failing
 * test says what to fix. Colour contrast is left to tokens.test.ts: jsdom computes no colours.
 */
export async function a11yViolations(root: Element = document.body): Promise<string[]> {
  const results = await axe.run(root, {
    runOnly: { type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa'] },
    rules: { 'color-contrast': { enabled: false } },
  });
  return results.violations.map(
    (violation) =>
      `${violation.id}: ${violation.help} (${violation.nodes.map((node) => node.target.join(' ')).join(', ')})`,
  );
}
