# Eval results

Scores of the assistant over `evals/questions.yaml`, from `uv run python -m app.evals.run --write` in `backend/` (ADR-031). Each case passes only if every fact is said, no forbidden claim is made, nothing is unsupported by the content, the citations are valid, the route is right and the language matches. The judge is a model with a written rubric, so a score moves a little between runs of the same code.

## Latest run: 2026-11-11, commit 1e3d496

Answers `gpt-5.6-luna`, guardrail `gpt-5.6-luna`, judge `gpt-5.6-luna`, embeddings `text-embedding-3-small`.

**28 of 41 cases passed** (0 not graded because of an error).

| Metric | Score |
|---|---|
| Fact recall | 86 % |
| Policy compliance | 100 % |
| Faithfulness | 100 % |
| Citation validity | 100 % |
| Routing accuracy | 100 % |
| Language match | 100 % |
| Latency p50 / p95 | 2.2 s / 2.9 s |
| Tokens per case (answer, guardrail and search) | 3361 |

| Category | Passed |
|---|---|
| ai | 2 of 6 |
| education | 1 of 1 |
| experience | 4 of 9 |
| injection | 2 of 2 |
| languages | 1 of 1 |
| logistics | 4 of 4 |
| off-topic | 2 of 2 |
| overview | 1 of 2 |
| policy | 6 of 8 |
| skills | 5 of 6 |

### Cases that failed

- `overview-en` (overview)
  - missing: focused on shipping AI into real products since 2023
- `current-roles` (experience)
  - missing: Full Stack Developer (AI) at Simbel IA Studio
  - missing: AI R&D Developer at Universidad Tecnológica Nacional
- `servime` (experience)
  - missing: a link to the product site, servime.net
- `simbel` (experience)
  - missing: Full Stack Developer (AI) since October 2023
- `leadership` (experience)
  - missing: Scrum and Kanban with Jira
- `teaching` (experience)
  - missing: teaching degree (Profesorado en Educación) from Universidad Tecnológica Nacional, 2017
- `unknown-skill` (skills)
  - missing: offers to forward the question to Leonardo
- `rag-assistant` (ai)
  - missing: the code is under NDA; an architecture walkthrough is available on request
- `ai-agents` (ai)
  - missing: Python, LangGraph, function calling and PostgreSQL
- `voice-avatars` (ai)
  - missing: back office on Supabase with Edge Functions
- `n8n` (ai)
  - missing: at Simbel IA Studio, n8n automation pipelines
  - missing: WhatsApp and Telegram chatbots
- `phone-number` (policy)
  - missing: the phone number from the site configuration, with a WhatsApp link
  - missing: the contact flow and his LinkedIn profile as other options
- `email-address` (policy)
  - missing: the contact flow and his LinkedIn profile as other options

Not run, because their agent arrives in Phase 6: job-fit-gaps, job-fit-injection, contact-request.

## History

| Date | Commit | Cases | Passed | Fact recall | Policy | Faithful | Citations | Routing | p95 s | Tokens/case |
|---|---|---|---|---|---|---|---|---|---|---|
| 2026-11-11 | 1e3d496 | 41 | 28 | 86 % | 100 % | 100 % | 100 % | 100 % | 2.9 | 3361 |
| 2026-11-11 | 1e3d496 | 41 | 20 | 90 % | 100 % | 59 % | 100 % | 100 % | 3.4 | 3348 |
