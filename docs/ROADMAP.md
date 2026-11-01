# Roadmap

CV-BOT-IA is a chat-first CV: recruiters open the site, see a short profile card, and ask an AI assistant anything about Leonardo's experience. The assistant answers with citations, analyses job offers against his profile, and forwards contact requests.

This file is the step-by-step guide for building it. Work happens one step at a time, and every phase ends with something reviewed, deployed or approved.

## How we work

- **One step = one branch = one pull request.** Branch names follow `<type>/<phase>.<step>-<short-name>`, e.g. `feat/3.2-backend-skeleton`.
- **A step is done when it meets the Definition of Done** in [the quality skill](../.claude/skills/quality-standards/SKILL.md), not when the code "works on my machine".
- **Tick the checkbox in this file** in the same PR that finishes the step.
- **New technical decision → new entry in [DECISIONS.md](DECISIONS.md)** explaining why.
- **Design before code.** The interface is built from the approved mockups documented in `docs/DESIGN.md` (step 2.6), not designed while coding.
- **Never skip ahead.** If a later step needs something earlier, go back and finish it first.

## Architecture at a glance

```
React + Vite + Tailwind (Hostinger, static)
        │  POST /chat  (Server-Sent Events)
        ▼
FastAPI + LangGraph (Railway)
        ├── Guardrail ──► Supervisor ──► Profile agent (RAG + citations)
        │                           ├──► Job-fit analyst
        │                           └──► Contact agent
        ├── OpenAI (fast model for routing, strong model for answers, embeddings)
        ├── Supabase Postgres + pgvector (hybrid search over case studies)
        └── Langfuse (traces) · evals in CI
```

---

## Phase 0 — Foundations

Goal: the idea, the decisions and the quality bar are written down before any code exists.

- [x] 0.1 Roadmap (this file)
- [x] 0.2 Quality standards skill + `CLAUDE.md`
- [x] 0.3 `docs/DECISIONS.md`: one short entry per decision taken so far (chat-first, two services instead of microservices, two-tier context + RAG, multi-agent with LangGraph, hosting split, third-person assistant, live avatar out of scope, privacy rules)
- [ ] 0.4 Buy the personal domain
- [ ] 0.5 Create accounts and API keys: OpenAI (models and embeddings, ADR-019), Railway, Supabase, Langfuse, email provider. Keys go to a password manager and to platform secrets, never to the repo
- [ ] 0.6 GitHub repo settings: public, branch protection on `main` (PR + green CI required)

**Done when:** anyone reading `docs/` understands what we build and why, and every account exists.

## Phase 1 — Content

Goal: one reviewed source of truth that both the page and the assistant read. The assistant can never be better than this content.

- [x] 1.1 `content/profile.yaml`: unified CV in EN/ES (fixes the inconsistencies between the two PDFs, no phone number)
- [x] 1.2 `content/policies.md`: how the assistant handles sensitive topics (salary, start date, citizenship, concurrent roles, English level, NDA work, unknown answers)
- [x] 1.3 `content/case-studies/_TEMPLATE.md`
- [ ] 1.4 Case studies, one per PR. Leonardo drafts in Spanish, then we edit them into English together:
  - [ ] ServiME
  - [ ] RAG document assistant
  - [ ] AI agent with tool use
  - [ ] Real-time conversational AI avatars
  - [ ] LLM pipelines with n8n
  - [ ] Leading an 8-developer team at Universidad Atlántida
- [x] 1.5 `evals/questions.yaml`: 30+ real recruiter questions with the facts a good answer must contain. These become the eval dataset in Phase 5
- [x] 1.6 Content schema + validation test (fails CI if `profile.yaml` breaks the schema or a case study misses a required section)
- [ ] 1.7 Assets:
  - [x] Professional profile photo (`content/assets/profile-photo.jpg`, without metadata)
  - [ ] CV PDFs (EN/ES) for download. They include the phone number, so they stay out of the repo (ADR-016)

**Done when:** Leonardo has reviewed every fact and the validation test passes.

## Phase 2 — Visual design

Goal: decide how the product looks and feels before writing interface code. Recruiters judge in seconds, so this phase gets the same care as the AI.

- [x] 2.1 Reference: LinkedIn's home feed and messaging, chosen by Leonardo as the single reference (what we take from it: ADR-017)
- [x] 2.2 Visual direction: an interactive mockup of the main screen (desktop + mobile) built with real content, approved by Leonardo (ADR-017)
- [x] 2.3 Visual identity: accent colour, light and dark palettes, typography, icon set, photo treatment, cover image, tone of the interface copy (ADR-018)
- [x] 2.4 High-fidelity mockups of every screen and state (13 state boards in the design canvas; their screenshots go into `DESIGN.md` in step 2.6):
  - [x] First load with suggested questions
  - [x] Streaming answer with citations
  - [x] Cards: project, experience timeline, skills, job-fit report
  - [x] Contact flow and confirmation
  - [x] Errors: network failure, rate limit, off-topic redirect
  - [x] Mobile and dark mode versions of all of the above
- [x] 2.5 Motion spec: what animates, how long and with which easing; reduced-motion fallback (ADR-020)
- [x] 2.6 `docs/DESIGN.md`: tokens, components, states and screenshots of the approved mockups. Phase 4 builds from this file

**Done when:** Leonardo has approved the final mockups and every state the interface can be in has a design.

## Phase 3 — Skeleton and CI/CD

Goal: an empty "hello world" travels from a push on `main` to production automatically.

- [x] 3.1 Monorepo layout: `frontend/`, `backend/`, `content/`, `evals/`, `docs/`
- [x] 3.2 Backend: FastAPI with `/health` and typed settings, on the Python project from 1.6 (`uv`, ruff, mypy strict, pytest)
- [x] 3.3 Frontend: Vite + React + TypeScript (strict), Tailwind, oxlint, Prettier, Vitest + Testing Library
- [x] 3.4 pre-commit hooks (format, lint, secret scanning)
- [ ] 3.5 GitHub Actions CI: add the frontend job (lint, type-check, test, build) next to the backend job from 1.6
- [ ] 3.6 Deploy: frontend to Hostinger by FTP, backend to Railway, both on merge to `main`; the phone number reaches both from deployment secrets (ADR-016)
- [ ] 3.7 DNS: domain → Hostinger, `api.` subdomain → Railway, HTTPS on both
- [ ] 3.8 PR template + issue templates

**Done when:** the production domain shows the frontend, `api.<domain>/health` answers, and CI is green.

## Phase 4 — Chat interface (mocked backend)

Goal: build the approved design with a fake server that streams pre-written answers, so the interface can be finished and tested before any AI exists.

- [ ] 4.1 Design tokens from `DESIGN.md` into CSS variables and the Tailwind theme; light and dark themes
- [ ] 4.2 API contract in `docs/API.md`: `POST /chat` and its SSE events (`token`, `citation`, `card`, `node`, `done`, `error`); `node` names the graph step that is working, for the live graph on the cover (ADR-020)
- [ ] 4.3 Mock server that streams fake answers following the contract, including slow, failing and very long responses
- [ ] 4.4 Layout: profile card + conversation; on mobile the card collapses into a header
- [ ] 4.5 Chat: streamed messages, Markdown, suggested questions, typing indicator, citations, retry on error, empty, loading and error states
- [ ] 4.6 Cards: project, timeline, skills, job-fit report
- [ ] 4.7 Motion and micro-interactions as specified in `DESIGN.md`
- [ ] 4.8 i18n EN/ES (English by default, follows the browser)
- [ ] 4.9 Accessibility: keyboard only, screen reader (`aria-live`), contrast, `prefers-reduced-motion`; axe checks in tests
- [ ] 4.10 SEO and sharing: meta tags, Open Graph image, favicon
- [ ] 4.11 Design QA: built UI compared side by side with the mockups on phone and desktop, in both themes; differences fixed or approved
- [ ] 4.12 Lighthouse ≥ 95 in every category

**Done when:** the interface looks like the approved mockups and feels finished on phone and desktop; only the answers are placeholders.

## Phase 5 — AI MVP: RAG chat

Goal: the real assistant answers questions about Leonardo with citations, safely and cheaply.

- [ ] 5.1 Ingestion: chunk case studies by heading, embed, upsert into Supabase pgvector. Idempotent, runs in CI when `content/` changes
- [ ] 5.2 Hybrid retrieval (full-text + vector) with unit tests
- [ ] 5.3 Profile agent: core profile in a cached system prompt + `search_docs` tool; every claim cites its source
- [ ] 5.4 Guardrail: prompt-injection and off-topic detection; `policies.md` enforced
- [ ] 5.5 Abuse and cost protection: rate limit per IP/session, max message length, CORS locked to the domain, daily spend cap
- [ ] 5.6 Langfuse tracing on every request (no personal data in traces)
- [ ] 5.7 Eval runner over `evals/questions.yaml` (faithfulness, citation correctness, policy compliance); record the baseline score
- [ ] 5.8 Connect the frontend to the real backend

**Done when:** it runs in production, the eval baseline is recorded in `evals/RESULTS.md`, and the prompt-injection test set passes.

## Phase 6 — Multi-agent

Goal: the assistant does more than answer; each agent exists because its task really differs.

- [ ] 6.1 LangGraph supervisor: typed state, fast-model router, guardrail as the entry node
- [ ] 6.2 Job-fit analyst (subgraph): pasted job offer → requirements → evidence from the profile → honest fit report
- [ ] 6.3 Contact agent: collects name, email, company and message, confirms, and emails a summary to Leonardo (anti-spam included)
- [ ] 6.4 Connect the agents to the cards built in 4.6 and to the live graph on the cover
- [ ] 6.5 Graph tests with fake models: routing, every node, error paths
- [ ] 6.6 Evals for routing accuracy and job-fit quality

**Done when:** the three agents work in production and their evals are above the agreed thresholds.

## Phase 7 — Quality and showcase

Goal: the repo is as impressive as the product.

- [ ] 7.1 Evals in CI: PRs that change prompts or content fail if the score drops below the threshold
- [ ] 7.2 End-to-end tests with Playwright (main flows, mocked LLM)
- [ ] 7.3 Visual regression tests: Playwright screenshots of key screens in both themes, so the design can't break unnoticed
- [ ] 7.4 Security pass: OWASP checklist, prompt-injection suite, dependency and secret scanning
- [ ] 7.5 README: hero GIF, architecture diagram, key decisions, eval metrics, run locally in 3 commands
- [ ] 7.6 Recorded demo of the AI avatar project, linked from the profile card
- [ ] 7.7 Launch: LinkedIn post, link in both CV PDFs

**Done when:** a tech lead can understand the project from the README in 2 minutes and run it locally in 5.

## Phase 8 — Optional: voice mode

- [ ] 8.1 Ask by microphone (speech-to-text) and hear the answer (text-to-speech), ideally with Leonardo's cloned voice
- [ ] 8.2 Cost review before enabling it publicly
