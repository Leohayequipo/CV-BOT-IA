<!-- Title in Conventional Commits form, e.g. "feat(frontend): stream answers in the chat" -->

## What & why

<!-- One paragraph, with the roadmap step it completes, e.g. "Roadmap step 4.5". -->

## How to test

<!-- Commands or steps a reviewer can follow. -->

## Screenshots

<!-- UI changes only: phone and desktop, light and dark. Delete this section otherwise. -->

## Evals

<!-- Only when prompts, content or retrieval change: scores before and after. Delete this section otherwise. -->

## Checklist

<!-- The Definition of Done from .claude/skills/quality-standards/SKILL.md -->

- [ ] Behaviour is covered by tests that would fail if the feature broke
- [ ] Quality gate is green for every touched app
- [ ] No `TODO` without an issue link, no commented-out code, no debug prints or `console.log`
- [ ] No secrets, keys or personal data (phone, salary) in the diff
- [ ] Errors are handled at the boundaries, and users see a friendly message instead of a stack trace
- [ ] UI matches `docs/DESIGN.md` on phone and desktop, in light and dark mode, with keyboard only
- [ ] Prompt or content changes: evals re-run, score not lower than before
- [ ] Docs updated: roadmap checkbox, decisions, API contract, README
