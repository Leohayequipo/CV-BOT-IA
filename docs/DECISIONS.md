# Decisions

Why CV-BOT-IA is built the way it is. Each entry records one decision, the alternatives considered and the trade-offs accepted, so a reviewer can judge the reasoning and not just the result.

**How this log works**

- Entries are numbered and dated. Accepted entries are not rewritten: to change a decision, add a new entry and mark the old one `Superseded by ADR-0XX`.
- A new framework, service or provider needs an entry here before it enters the code. Day-to-day tooling (linters, formatters, test runners) is defined in the [quality standards](../.claude/skills/quality-standards/SKILL.md).

## Summary

| ADR | Decision |
|---|---|
| 001 | Chat-first CV instead of a classic portfolio |
| 002 | Two services in a monorepo, not microservices |
| 003 | React + Vite static site, not Next.js |
| 004 | Python and FastAPI for the backend |
| 005 | Frontend on Hostinger, backend on Railway |
| 006 | Claude as the LLM, with a model per kind of task (superseded by 019) |
| 007 | Two-tier context: profile in the prompt, case studies through RAG |
| 008 | Postgres with pgvector on Supabase, with hybrid search |
| 009 | Multi-agent graph with LangGraph |
| 010 | Evals and tracing as part of the product |
| 011 | The assistant speaks about Leonardo in the third person |
| 012 | Privacy: publish only what a recruiter needs (phone rule superseded by 016) |
| 013 | No live video avatar; a recorded demo instead |
| 014 | Design before code, inspired by LinkedIn |
| 015 | Content as the single source of truth, English first |
| 016 | Phone number visible on the site, kept out of the repo |
| 017 | Visual direction: LinkedIn's three-column layout |
| 018 | Visual identity: teal accent, system fonts and Lucide icons |
| 019 | OpenAI for the language models and the embeddings |
| 020 | Motion: short CSS animations with a reduced-motion version |
| 021 | A stateless chat API, and contact sent only on confirmation |
| 022 | Mock answers from the real backend, built from the content |
| 023 | The site reads the profile from a JSON copy the backend exports |

---

## ADR-001 · Chat-first CV instead of a classic portfolio

*Accepted · 2026-10-30*

**Decision:** the product is a conversation. The page shows a compact profile card (photo, headline, work authorisation, links, CV download) next to a chat that opens with suggested questions.

**Why:** portfolio sites look alike and make recruiters hunt for what they need. A chat lets them ask exactly that, and it demonstrates the AI engineering this project is meant to prove.

**Alternatives considered:** a classic multi-section portfolio; a portfolio with a chat widget in a corner, where the chat becomes an afterthought.

**Trade-offs:** some recruiters won't type. The profile card, the suggested questions and the PDF download make the essentials visible in seconds without chatting.

## ADR-002 · Two services in a monorepo, not microservices

*Accepted · 2026-10-30*

**Decision:** one static frontend and one Python API, in a single repository with `frontend/`, `backend/`, `content/`, `evals/` and `docs/`.

**Why:** one developer and one core feature. Microservices would add network hops, deploys and failure modes without solving a real problem here. A monorepo lets the API contract, the content and both apps change together in one reviewed PR.

**Alternatives considered:** microservices (for example one service per agent plus an ingestion service); a separate repository per app.

**Trade-offs:** two deploy targets instead of one. Clear module boundaries inside the backend keep any part extractable if it ever needs to scale on its own.

## ADR-003 · React + Vite static site, not Next.js

*Accepted · 2026-10-30*

**Decision:** the frontend is a React + TypeScript single-page app built with Vite into static files.

**Why:** all server logic lives in the Python API, so the server features of Next.js would go unused. Static files deploy to the existing Hostinger hosting with no server process to run.

**Alternatives considered:** Next.js; Astro.

**Trade-offs:** no server-side rendering. It is a single page, so static meta tags and an Open Graph image cover search engines and link previews.

## ADR-004 · Python and FastAPI for the backend

*Accepted · 2026-10-30*

**Decision:** Python with FastAPI, with dependencies managed by uv.

**Why:** the AI ecosystem lives in Python (LangGraph, provider SDKs, eval tooling), and it is the stack of the roles Leonardo targets. FastAPI adds typed validation with Pydantic, async streaming for Server-Sent Events and generated API docs.

**Alternatives considered:** PHP/Laravel on the existing Hostinger hosting (no extra cost, and a stack Leonardo has used for years); Node.js.

**Trade-offs:** the API needs its own hosting (ADR-005).

## ADR-005 · Frontend on Hostinger, backend on Railway

*Accepted · 2026-10-30*

**Decision:** the static frontend is served from Leonardo's existing Hostinger shared hosting. The API runs on Railway under the `api.` subdomain of his personal domain.

**Why:** Hostinger is already paid for, but its shared plans can't run Python processes. Railway deploys straight from the repository, costs around USD 5 a month at this load and doesn't sleep by default, so the first answer is quick.

**Alternatives considered:** a Hostinger VPS for everything (more operations work: OS updates, reverse proxy, certificates); Render's free tier (the service sleeps when idle and the next request waits tens of seconds, a poor first impression for a recruiter); Fly.io.

**Trade-offs:** two providers and a cross-origin setup, with CORS locked to the domain. CI deploys both, so shipping is still a single merge.

## ADR-006 · Claude as the LLM, with a model per kind of task

*Accepted · 2026-10-30 · Superseded by ADR-019*

**Decision:** Anthropic's Claude models, chosen per task: a fast, low-cost model for the guardrail and the router, and a stronger one for answers and job-fit analysis. The static part of the prompt uses prompt caching. Model IDs live in configuration, not in code.

**Why:** the guardrail and the router run on every message and need speed, not depth; answers need quality. Caching the system prompt and the profile cuts cost and latency on every request. Leonardo's production work already uses OpenAI and Gemini, so this project also shows range across providers.

**Alternatives considered:** one model for everything (simpler, but it pays top price for simple classification); OpenAI or Gemini models.

**Trade-offs:** two models to evaluate instead of one. Provider calls go through a single client module, so changing provider stays contained.

## ADR-007 · Two-tier context: profile in the prompt, case studies through RAG

*Accepted · 2026-10-30*

**Decision:** the core profile (`content/profile.yaml`) is always in the cached system prompt. Case studies are chunked, embedded and retrieved on demand, and every claim cites its source.

**Why:** the profile is small and relevant to almost every question, so retrieving it would only add ways to fail. Case studies are long and numerous, and a question needs only a few sections of them, so retrieval keeps prompts small and citations precise. RAG is there because the knowledge base needs it, not as decoration.

**Alternatives considered:** everything in the prompt (fine for a two-page CV, but it grows with every case study and loses section-level citations); retrieval for everything (adds the risk of missing basic facts such as the current role).

**Trade-offs:** an ingestion pipeline to maintain. It is idempotent and runs in CI whenever `content/` changes.

## ADR-008 · Postgres with pgvector on Supabase, with hybrid search

*Accepted · 2026-10-30*

**Decision:** chunks are stored in Postgres with pgvector on Supabase and retrieved with hybrid search: full-text and vector similarity merged with reciprocal rank fusion.

**Why:** recruiters ask with exact names ("FilamentPHP", "n8n", "LangGraph"), where keyword search beats embeddings, and with vague intent ("has he led a team?"), where embeddings win. Postgres covers both in one query, the index survives redeploys, the free tier is enough, and Leonardo already works with Supabase.

**Alternatives considered:** an in-memory index (enough for this volume, but keyword search and persistence would have to be built by hand); a dedicated vector database such as Pinecone or Qdrant (another service with no extra benefit here).

**Trade-offs:** a managed database dependency. Ingestion can rebuild it from `content/` at any time.

## ADR-009 · Multi-agent graph with LangGraph

*Accepted · 2026-10-30*

**Decision:** a LangGraph graph with a guardrail as the entry node, a supervisor that routes, and three agents: profile Q&A (RAG with citations), job-fit analyst and contact.

**Why:** plain Q&A would fit in one model call, but the other two tasks differ in prompt, tools, model and risk. Job-fit analysis takes several steps: extract the requirements, find evidence, write the report. The contact agent has a side effect (it emails Leonardo), so its tool should exist only on that path and behind a confirmation. LangGraph makes the flow an explicit, typed state machine whose routing and nodes can be unit-tested with fake models.

**Alternatives considered:** a single agent with every tool (one ever-growing prompt, the email tool exposed on every turn, quality hard to measure per task); CrewAI (autonomous role-based agents that talk to each other: more tokens and less predictability for a flow that is known in advance).

**Trade-offs:** more moving parts than a single call. Graph tests and routing evals keep them in check.

## ADR-010 · Evals and tracing as part of the product

*Accepted · 2026-10-30*

**Decision:** a versioned dataset of recruiter questions in `evals/`, scored on fact recall, hallucination, citation validity, policy compliance and routing accuracy. CI blocks PRs that lower the score. Langfuse traces every request.

**Why:** without measurement, every prompt change is a guess. A public score history is also the strongest evidence of quality this repo can show. Langfuse is open source, has a free tier, and Leonardo already uses it in his RAG work.

**Alternatives considered:** manual testing only; LangSmith (also solid; Langfuse wins on being open source and self-hostable).

**Trade-offs:** evals call real models and cost money, so they run only when prompts, content or retrieval change.

## ADR-011 · The assistant speaks about Leonardo in the third person

*Accepted · 2026-10-30*

**Decision:** it introduces itself as Leonardo's AI assistant and says "Leonardo built…", never "I built…".

**Why:** it is honest about being an AI, it doesn't make first-person commitments on Leonardo's behalf, and it keeps a clear line between what the content says and what Leonardo would say in an interview.

**Alternatives considered:** an "AI Leonardo" speaking in the first person (more playful, but it blurs who is talking).

**Trade-offs:** slightly less personal; the tone of the interface makes up for it.

## ADR-012 · Privacy: publish only what a recruiter needs

*Accepted · 2026-10-30 · The phone rule is superseded by ADR-016*

**Decision:** no phone number anywhere in the site or the repo. The assistant doesn't give salary figures or a start date; it offers a direct conversation instead. The rules live in `content/policies.md`, the guardrail enforces them, evals test them, and traces redact contact details.

**Why:** the repo and the site are public, and anything published gets scraped. Salary and availability depend on the role and belong in a real conversation.

**Alternatives considered:** publishing everything in the PDF CV.

**Trade-offs:** some recruiters want those answers immediately; the contact agent keeps that conversation one step away.

## ADR-013 · No live video avatar; a recorded demo instead

*Accepted · 2026-10-30*

**Decision:** no real-time video avatar in the product. A recorded demo of Leonardo's avatar project is linked from the profile card.

**Why:** as of October 2026, LiveAvatar's free plan offers 10 credits a month (a few minutes in total), 2-minute sessions, a watermark and stock avatars only; a custom avatar needs the USD 99/month plan. A feature that runs out after a few visitors would hurt more than it helps.

**Alternatives considered:** the free plan with a stock avatar; the paid plan.

**Trade-offs:** less spectacle on first load. LiveAvatar's "Avatar Only" mode could later sit on top of the same agents, and voice mode (Phase 8) is a cheaper middle ground.

## ADR-014 · Design before code, inspired by LinkedIn

*Accepted · 2026-10-30*

**Decision:** a dedicated design phase produces approved mockups and `docs/DESIGN.md` before any interface code. The visual language is inspired by LinkedIn's profile and messaging screens, with its own accent colour and without LinkedIn's logo or name.

**Why:** recruiters already know how to read that layout, so the page is understood at a glance. Designing while coding leads to inconsistent results; mockups let Leonardo compare and approve the look before it costs code.

**Alternatives considered:** a dark "AI product" look; a terminal look; designing during implementation.

**Trade-offs:** a phase with nothing running to show. Visual regression tests keep the approved design from drifting afterwards.

## ADR-015 · Content as the single source of truth, English first

*Accepted · 2026-10-30*

**Decision:** everything about Leonardo lives in `content/` (a YAML profile plus Markdown policies and case studies), read by both the interface and the assistant and validated by tests. The interface and the repo are English first, with Spanish as the second language; the assistant answers in the user's language.

**Why:** with one place to correct a fact, the page and the assistant can't contradict each other. The target audience is recruiters in the EU.

**Alternatives considered:** texts hard-coded in the frontend; separate content per language.

**Trade-offs:** content changes go through PRs, which is slower than editing a web page, but every change is reviewed and evaluated.

## ADR-016 · Phone number visible on the site, kept out of the repo

*Accepted · 2026-10-30 · Supersedes the phone rule of ADR-012*

**Decision:** the site shows Leonardo's phone number with a WhatsApp link, and the assistant shares it when someone asks how to reach him. The number never enters the repository: the frontend build and the API read it from deployment configuration (a GitHub Actions secret and a Railway variable). The privacy test still fails if a phone number appears in `content/` or `evals/`.

**Why:** Leonardo wants recruiters to reach him directly, including by WhatsApp. Keeping the number in configuration instead of Git means it never becomes part of the public history and can be removed with a redeploy.

**Alternatives considered:** keeping the number off the site (ADR-012: less spam, but one more step for recruiters); writing it in `profile.yaml` (simplest, but permanent in the public Git history).

**Trade-offs:** the live site exposes the number to scrapers and possible spam. Local development uses a placeholder from `.env.example`. The downloadable CV PDFs include the number, so they aren't committed either.

## ADR-017 · Visual direction: LinkedIn's three-column layout

*Accepted · 2026-10-30*

**Decision:** the main screen follows LinkedIn's home layout. The profile card sits on the left, the chat takes the centre where LinkedIn has the feed, and the right column holds shortcut cards: suggested questions and recent experience. Messages look like LinkedIn messaging (avatar, name and time, no bubbles), and the message box is a pill like LinkedIn's "Start a post". On a phone, the profile collapses into a header with contact buttons above the chat. The page uses a warm grey background, white cards, system fonts and its own "LM" monogram. Leonardo approved an interactive mockup of this direction for desktop and mobile; it lives in a design canvas, and its screenshots go into `docs/DESIGN.md` in step 2.6.

**Why:** Leonardo chose LinkedIn as the single reference. Recruiters spend their day there, so every element is where they expect it. Refining one direction replaced the two or three the roadmap planned.

**Alternatives considered:** two or three contrasting directions, one of them built on ServiME's palette. That palette survives as an accent option for step 2.3.

**Trade-offs:** the look is familiar rather than distinctive, so the accent colour, the cover image and the motion (steps 2.3 to 2.5) have to carry the personality. Being this close to LinkedIn also means the site must never use its logo, its name or its exact brand colours.

## ADR-018 · Visual identity: teal accent, system fonts and Lucide icons

*Accepted · 2026-10-31*

**Decision:** the accent colour is teal (`#0F6E78` in light mode, `#62C6CD` in dark mode), on a neutral grey tinted with the same hue instead of ADR-017's warm grey. Teal marks what can be clicked and the facts a recruiter should see first, such as EU citizenship. A project's own brand colours appear only inside its project card: ServiME's card has a band and a logo tile in its green, orange and cream, while its text and links stay teal. Text uses the system fonts in three weights, and icons come from Lucide. Leonardo's photo on its own stands for him; with a teal badge it stands for the assistant. The cover of the profile card draws the assistant's real graph (guardrail, supervisor and three agents) over a dot pattern, as inline SVG that follows the theme. The Spanish copy uses voseo, in the interface and in the assistant's answers. All text meets WCAG AA contrast in both themes, and control borders reach 3:1. The identity sheet lives in the design canvas next to the mockups; its tokens go into `docs/DESIGN.md` in step 2.6.

**Why:** teal is the accent of Leonardo's CV PDFs, so the site and the PDF read as one brand, and it keeps a page shaped like LinkedIn from looking like a blue copy of it. ServiME's palette across the whole site would make it read as a company page and push his other roles into the background. System fonts need no download, which helps the Lighthouse target (step 4.12). Lucide is open source (ISC licence), ships one icon per import and matches the line style of the mockups. The badge keeps visitors from thinking Leonardo himself is typing (ADR-011). Leonardo chose voseo, his own variety of Spanish, over neutral *tú*.

**Alternatives considered:** a blue accent close to LinkedIn's, or ServiME's green, both compared in the mockup; a web font such as Inter; hand-drawn SVG icons; a photo as the cover; neutral *tú* in Spanish.

**Trade-offs:** system fonts look slightly different on each operating system, and Lucide adds a frontend dependency. Voseo may sound informal to recruiters in Spain; since English is the default, it only reaches visitors whose browser is set to Spanish.

## ADR-019 · OpenAI for the language models and the embeddings

*Accepted · 2026-10-31 · Supersedes ADR-006*

**Decision:** OpenAI provides both the language models and the embeddings. ADR-006's split by task stays: a fast, low-cost model for the guardrail and the router, and a stronger one for answers and job-fit analysis. Model IDs live in configuration and are chosen with the evals in Phase 5. Every provider call goes through a single client module.

**Why:** Leonardo chose OpenAI for the project's account. One account and one key cover both the chat and the embeddings, which settles the open embeddings decision and leaves one provider fewer to set up in step 0.5. OpenAI caches repeated prompt prefixes automatically, so keeping the profile and the policies at the start of the prompt still cuts cost and latency, as ADR-006 planned. It is also the provider Leonardo already uses in his production work.

**Alternatives considered:** keeping Claude (ADR-006), whose argument was showing a provider beyond the ones in his production work; Gemini; a separate provider for the embeddings.

**Trade-offs:** the repo no longer shows that range across providers; since calls go through one client module, switching provider stays a contained change. The stored vectors belong to one embedding model, so changing it means running the ingestion again, which is idempotent (ADR-007).

## ADR-020 · Motion: short CSS animations with a reduced-motion version

*Accepted · 2026-10-31*

**Decision:** motion uses three durations (120, 200 and 320 ms) and three easing curves: one for what enters, one for what leaves, and one for what moves or loops. What enters fades in while rising 8 px (12 px for cards), and what leaves fades out in 120 ms. Nothing lasts longer than 320 ms except the waiting indicators: the typing dots, the streaming caret and the retry spinner. The page load, each streamed word and the theme switch don't animate. Under `prefers-reduced-motion` nothing moves, scales or rotates: only opacity and colour change, in 120 ms at most, and nothing loops. While the assistant thinks, the cover of the profile card lights up the path the question takes through the graph (guardrail, supervisor, agent), so the API streams which node is working (step 4.2). Animations are plain CSS transitions and keyframes, with no animation library. The motion sheet lives in the design canvas; its tokens go into `docs/DESIGN.md` in step 2.6.

**Why:** the visitor is reading, so motion should show what changed and never make them wait; short durations keep the chat feeling fast. CSS covers every animation in the sheet with no extra JavaScript, animates opacity and transforms without blocking the main thread, and handles reduced motion with a single media query. The live graph turns the architecture of ADR-009 into something a visitor can watch, which is what this project has to prove. Leonardo approved the sheet, including the live graph.

**Alternatives considered:** an animation library such as Motion (formerly Framer Motion), which helps with exit and layout animations but adds JavaScript for effects CSS already covers; no motion at all; the typing dots alone, without the live graph.

**Trade-offs:** a CSS exit animation needs the element to stay mounted until its fade ends. The live graph adds an event to the API contract, and it only shows on desktop, where the cover is visible.

## ADR-021 · A stateless chat API, and contact sent only on confirmation

*Accepted · 2026-10-31*

**Decision:** `POST /chat` streams the answer as Server-Sent Events, and the site sends the recent history with every question, so the server keeps no conversation state. A random `session_id` exists only for rate limiting. The email to Leonardo goes out through a separate `POST /contact`, which the site calls only when the visitor confirms the summary. The contract lives in [`API.md`](API.md).

**Why:** without server-side state there is no session store to run, expire or protect, any backend instance can answer any request, and no conversation is kept on the server (ADR-012). The history limit keeps the cost of a request bounded. Sending email is the only action with a side effect, so it waits for a person's explicit click instead of a model's decision; a prompt injection can't trigger it, which is the confirmation ADR-009 asked for. SSE fits a one-way stream of events and works over plain HTTP.

**Alternatives considered:** keeping conversations on the server with a LangGraph checkpointer in Postgres, which allows resuming but stores every conversation and adds a table to manage; WebSockets, two-way but heavier than this needs; letting the contact agent send the email when the visitor writes "yes".

**Trade-offs:** requests grow with the history, up to its limit. Reloading the page starts a new conversation. A visitor could alter the history the site sends, but that only affects their own conversation, and the guardrail treats history as untrusted input.

---

## ADR-022 · Mock answers from the real backend, built from the content

*Accepted · 2026-10-31*

**Decision:** until the agents exist (Phase 5), the backend's real `POST /chat` answers from scripts in `backend/app/agents/mock.py`. The request checks, the error responses, CORS and the event stream are the production code; only the part that writes the answer is a stand-in. The scripts build every answer from `content/`, and a message such as `mock: slow` picks the cases a real model can't produce on demand: a slow answer, a very long one, a failure partway through and the question limit. `POST /contact` accepts confirmed messages without sending them until the email provider arrives (step 6.3). The stream uses FastAPI's built-in Server-Sent Events, with no extra dependency.

**Why:** the site talks to the backend over the same HTTP, streaming and CORS it will use in production, so Phase 4 finds integration problems early, and Phase 5 replaces one module instead of a fake server. The scripts can show the designed states on purpose, which a real model can't do reliably. Building the answers from `content/` means even the placeholders say only true things about Leonardo; the job-fit report and the contact summary reuse the fictional samples of the approved designs, since producing them needs a model.

**Alternatives considered:** Mock Service Worker in the browser, which needs no backend but skips the real network path and repeats the contract's rules in TypeScript (it remains the tool for the site's own integration tests); a separate mock server generated from the contract, one more thing to run that would drift from the real one.

**Trade-offs:** working on the site needs the backend running, one `uv run` command. The scripts pick answers by keywords, so a question in other words gets the general answer.

---

## ADR-023 · The site reads the profile from a JSON copy the backend exports

*Accepted · 2026-11-02*

**Decision:** `uv run python -m app.content.export` (in `backend/`) writes `content/profile.yaml` to `frontend/src/content/profile.json`, which the site imports when it's built. The copy is committed, and a test in `backend/tests/content` fails while it differs from the profile, so CI and the pre-commit hook catch a forgotten export. The export adds what both apps need computed the same way: each company's initials and each role's period in English and Spanish. The site's photo, `frontend/src/assets/profile-photo.webp`, is a 160 px square derived from `content/assets/profile-photo.jpg` with the framing of the approved mockups.

**Why:** ADR-015 asks the page and the assistant to read the same content. The backend already loads and validates it, so the site reuses that work instead of adding a YAML parser. TypeScript infers the exact shape of the imported JSON, so a renamed key fails the type check. Dates and initials come from the same Python functions as the cards, so the profile column and the chat can't format them differently. The photo shrinks from 255 kB to about 4 kB, which the Lighthouse target needs (step 4.12).

**Alternatives considered:** parsing the YAML in the site with a library and a Vite plugin, which adds a dependency and hand-written types; serving the profile from the API, which would leave the page empty until the backend answers and hide it from search engines; generating the JSON during each build, which would make the frontend build need Python.

**Trade-offs:** a generated file lives in the repo, guarded by the test. Changing the photo means deriving the WebP again by hand; it changes rarely.

---

## Open decisions

| Decision | When |
|---|---|
| Personal domain name | Step 0.4 |
| Email provider for the contact agent | Step 0.5 |
| CV PDFs: generated from `profile.yaml` at build time, or uploaded by hand | Step 1.7 |
| Speech-to-text and text-to-speech providers | Phase 8 |
