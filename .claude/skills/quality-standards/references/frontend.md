# Frontend standards (React + Vite + TypeScript + Tailwind)

The interface is the first thing a recruiter judges, in under 30 seconds and often on a phone. It must feel fast, calm and finished.

## Toolchain

- Latest stable React, Vite and Tailwind. `npm` with a committed `package-lock.json`.
- TypeScript `strict: true` plus `noUncheckedIndexedAccess`. No `any`; use `unknown` and narrow it.
- ESLint (typescript-eslint, react-hooks, jsx-a11y) + Prettier.
- Vitest + Testing Library + `@testing-library/user-event` + MSW + `vitest-axe`. Playwright for end-to-end tests.

## Layout

```
frontend/src/
├── app/            # App shell, providers, routing (if ever needed)
├── features/
│   ├── chat/       # components, hooks, SSE client, state, tests
│   └── profile/    # profile card
├── components/ui/  # small reusable primitives (Button, Card, Avatar…)
├── lib/            # framework-free helpers (formatters, sse parser)
├── i18n/           # en.ts, es.ts and a typed t()
└── styles/         # tokens.css (CSS variables) + Tailwind entry
```

Organise by feature. Tests sit next to the code: `ChatInput.tsx` + `ChatInput.test.tsx`.

## Components and state

- Function components with typed props; one component per file; named exports.
- Keep components presentational and move logic into hooks (`useChat`, `useSuggestedQuestions`).
- Chat state lives in a `useReducer` with explicit actions (`send`, `token`, `citation`, `card`, `node`, `done`, `error`). Don't add a state library unless a real need appears.
- Streaming: `fetch` + `ReadableStream` with a small tested SSE parser in `lib/`. `EventSource` can't POST. Support cancel via `AbortController`.
- Never render model output as raw HTML. Use a Markdown renderer with HTML disabled, and only `http(s)` links.

## Design system

- **`docs/DESIGN.md` is the source of truth.** Build what the approved mockups show. A visual change that isn't in `DESIGN.md` needs Leonardo's approval first, and then gets added there.
- **Tokens first.** Colours, radii, shadows and font sizes are CSS variables in `tokens.css`, mapped into Tailwind's theme. Components use semantic names (`bg-surface`, `text-muted`, `ring-accent`), never raw hex values.
- **LinkedIn-inspired, not a copy:** light grey canvas, white cards, clear hierarchy, our own accent colour, no LinkedIn logo or name.
- Light and dark themes from day one, following `prefers-color-scheme`.
- The spacing, radii and type scale in `DESIGN.md`, with system fonts only (ADR-018).

## Polish checklist (what makes it stand out)

- Every async view has designed **empty, loading, streaming, error and retry** states. A spinner alone is not a design.
- Streaming text appears smoothly, the view auto-scrolls only if the user is already at the bottom, and a "jump to latest" button appears otherwise.
- Suggested questions on first load, so nobody faces an empty box.
- Motion follows the spec in `DESIGN.md` (ADR-020): the 120, 200 and 320 ms duration tokens, CSS only. Under `prefers-reduced-motion`, keep only opacity and colour changes of up to 120 ms, with no loops.
- Visible focus rings, generous hit targets (≥ 44px), and no layout shift while streaming.
- Copy is short, warm and professional, in both languages.

## Accessibility (WCAG 2.2 AA)

- Semantic HTML first (`button`, `form`, `main`, `nav`); ARIA only when HTML can't express it.
- The message list is a polite live region, announcing complete messages rather than every token.
- Everything works with the keyboard: Enter sends, Shift+Enter adds a new line, Esc closes overlays, and focus returns to the input after sending.
- Contrast ≥ 4.5:1 for text in both themes. Images have alt text.
- `vitest-axe` assertions in component tests; Playwright + axe on the main page.

## Performance budget

- Lighthouse ≥ 95 on Performance, Accessibility, Best Practices and SEO (mobile).
- Initial JS ≤ 150 kB gzipped. Lazy-load anything not needed for the first paint (Markdown renderer, cards).
- Self-host fonts with `font-display: swap`; serve images as AVIF/WebP with explicit sizes.

## Testing patterns

```tsx
it('sends the question when a suggestion is clicked', async () => {
  const user = userEvent.setup();
  render(<Chat />);

  await user.click(screen.getByRole('button', { name: /what ai projects/i }));

  expect(await screen.findByText(/rag document assistant/i)).toBeInTheDocument();
});
```

- Query by role, label and text, the way a user finds things. Avoid test IDs unless there is no accessible handle.
- Mock the network with MSW handlers that stream SSE events according to `docs/API.md`.
- Visual regression: Playwright screenshots of key screens (light/dark, mobile/desktop). An intended visual change updates the baseline in the same PR, with before/after images in the description.
