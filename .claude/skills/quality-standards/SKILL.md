---
name: quality-standards
description: Engineering standards for the CV-BOT-IA repo (React + Vite + TypeScript frontend, Python FastAPI + LangGraph backend, RAG, evals). Use this skill whenever you write, change, test or review anything in this repository, including code, tests, prompts, content files, CI workflows, docs and PR descriptions, and whenever you start or finish a step of docs/ROADMAP.md. Use it even for small changes, since every file in this public portfolio repo is a sample of Leonardo's work.
---

# Quality standards for CV-BOT-IA

This repo is Leonardo's flagship portfolio project. His client AI work is under NDA, so tech leads will judge his skills by reading **this** code: the tests, the commit history, the README and the reasoning in `docs/DECISIONS.md`. Optimise for a reviewer who opens a random file and asks "would I want this person on my team?".

That makes the bar different from a normal side project:

- **Simple and justified beats clever.** Every dependency and abstraction must have a reason a reviewer would accept. If you cannot explain why something exists in one sentence, it should not exist yet.
- **Visible quality.** Tests, types, evals and docs are part of the product, not chores after it.
- **Honest.** The assistant must never invent facts about Leonardo, and the code must never pretend to do more than it does.

## Workflow for every roadmap step

1. Read the step in `docs/ROADMAP.md` and any related entries in `docs/DECISIONS.md`.
2. Create a branch: `<type>/<phase>.<step>-<short-name>` (e.g. `feat/4.5-chat-streaming`).
3. Plan small. If the step needs more than ~400 changed lines, propose splitting it.
4. Write tests with the code, not after. For bugs, write the failing test first.
5. Run the quality gate for every app you touched (below). Fix everything, don't silence it.
6. Update docs in the same change: tick the roadmap checkbox, add a decision entry if you chose between alternatives, update `docs/API.md` if the contract changed, update the README if setup changed.
7. Commit with Conventional Commits and open a PR using the template.

Ask Leonardo before: adding a dependency not already named in `DECISIONS.md`, changing the API contract, changing anything in `content/` (those are facts about a real person), or anything that costs money.

## Definition of Done

A step is done only when all of these hold:

- [ ] Behaviour is covered by tests that would fail if the feature broke
- [ ] Quality gate is green for every touched app
- [ ] No `TODO` without an issue link, no commented-out code, no debug prints or `console.log`
- [ ] No secrets, keys or personal data (phone, salary) anywhere in the diff
- [ ] Errors are handled at the boundaries, and the user sees a friendly message instead of a stack trace
- [ ] UI changes match `docs/DESIGN.md` and work on mobile and desktop, in light and dark mode, with keyboard only
- [ ] Prompt or content changes: evals re-run, score not lower than before
- [ ] Docs updated (roadmap checkbox, decisions, API contract, README as needed)

## Quality gate

Run from the repo root once the apps exist (Phase 3 sets these scripts up, so keep them working):

```bash
# backend
cd backend && uv run ruff format --check . && uv run ruff check . && uv run mypy . && uv run pytest

# frontend
cd frontend && npm run format:check && npm run lint && npm run typecheck && npm run test -- --run && npm run build

# content
cd backend && uv run pytest tests/content
```

CI runs exactly these commands, so a green local gate means a green PR.

## Testing strategy

Aim for confidence, not a coverage number. Test the behaviour a user or caller relies on, through the public interface, so refactors don't break tests.

| Layer | Tool | What to test |
|---|---|---|
| Backend unit | pytest | Pure logic: chunking, retrieval scoring, policy rules, prompt building, state transitions |
| Backend API | pytest + httpx `AsyncClient` | Endpoints, validation errors, SSE event order, rate limiting, CORS |
| Agents/graph | pytest + fake chat model | Routing decisions, each node in isolation, tool calls, error paths |
| Frontend unit | Vitest + Testing Library | Components by role and visible text, hooks, the SSE parser |
| Frontend integration | Vitest + MSW | Full chat flow against a mocked streaming API |
| End-to-end | Playwright | Core journeys in a real browser, with the LLM mocked |
| AI quality | eval runner (`evals/`) | Faithfulness, citations, policy compliance, routing accuracy |

Rules that keep the suite trustworthy:

- **Unit and integration tests never call a real LLM or embedding API.** They would be slow, flaky and cost money. Use fakes, and keep real-model checks in evals.
- **Evals are not tests.** Tests are deterministic and gate every PR. Evals measure quality with real models and gate only PRs that touch prompts, content or retrieval.
- Name tests after behaviour: `test_salary_question_is_redirected_to_contact`, not `test_policy_3`.
- One reason to fail per test. Arrange-Act-Assert. No sleeps; use fake timers or events.
- Target ~85% line coverage on `backend/app` core logic as a smoke alarm, not a goal.

## Reference guides

Read the one that matches what you are touching:

- `references/backend.md`: Python, FastAPI, project layout, errors, logging, typing
- `references/frontend.md`: React, TypeScript, Tailwind, design polish, accessibility, performance
- `references/ai.md`: prompts, LangGraph, RAG, guardrails, prompt injection, cost, evals, observability
- `references/git-ci.md`: branches, commits, PRs, CI/CD, secrets, deploys

## Language

Code, comments, docs, commits and PRs are in English, because the audience is international recruiters and tech leads. Talk to Leonardo in Spanish.
