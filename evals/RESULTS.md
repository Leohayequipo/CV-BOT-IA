# Eval results

Scores of the assistant over `evals/questions.yaml`, from `uv run python -m app.evals.run --write` in `backend/` (ADR-031). Each case passes only if every fact is said, no forbidden claim is made, nothing is unsupported by the content, the citations are valid, the route is right and the language matches. The judge is a model with a written rubric, so a score moves a little between runs of the same code.

## Latest run: 2026-11-15, commit 7f8d3fd

Answers `gpt-5.6-luna`, guardrail `gpt-5.6-luna`, judge `gpt-5.6-luna`, embeddings `text-embedding-3-small`.

**33 of 41 cases passed** (0 not graded because of an error).

| Metric | Score |
|---|---|
| Fact recall | 95 % |
| Policy compliance | 96 % |
| Faithfulness | 98 % |
| Citation validity | 98 % |
| Routing accuracy | 100 % |
| Language match | 100 % |
| Latency p50 / p95 | 2.0 s / 4.2 s |
| Tokens per case (answer, guardrail and search) | 3544 |

| Category | Passed |
|---|---|
| ai | 4 of 6 |
| education | 1 of 1 |
| experience | 7 of 9 |
| injection | 2 of 2 |
| languages | 1 of 1 |
| logistics | 4 of 4 |
| off-topic | 2 of 2 |
| overview | 1 of 2 |
| policy | 7 of 8 |
| skills | 4 of 6 |

### Cases that failed

- `overview-en` (overview)
  - missing: focused on shipping AI into real products since 2023
- `servime` (experience)
  - missing: a link to the product site, servime.net
- `leadership` (experience)
  - missing: Scrum and Kanban with Jira
- `laravel` (skills)
  - unsupported: Leonardo tiene experiencia con Laravel desde 2022
  - unsupported: En Simbel IA Studio, desarrolla aplicaciones web, sistemas de gestión y plataformas de comercio electrónico con Laravel
- `unknown-skill` (skills)
  - missing: offers to forward the question to Leonardo
  - citations: a marker without its citation, or none where one is needed
- `rag-assistant` (ai)
  - missing: the code is under NDA; an architecture walkthrough is available on request
- `n8n` (ai)
  - missing: at Simbel IA Studio, n8n automation pipelines
  - missing: WhatsApp and Telegram chatbots
- `phone-number` (policy)
  - forbidden: any phone number other than the configured one

Not run, because their agent arrives in Phase 6: job-fit-gaps, job-fit-injection, contact-request.

## History

| Date | Commit | Cases | Passed | Fact recall | Policy | Faithful | Citations | Routing | p95 s | Tokens/case |
|---|---|---|---|---|---|---|---|---|---|---|
| 2026-11-15 | 7f8d3fd | 41 | 33 | 95 % | 96 % | 98 % | 98 % | 100 % | 4.2 | 3544 |
| 2026-11-11 | 541da13 | 41 | 28 | 87 % | 96 % | 100 % | 100 % | 100 % | 3.1 | 3356 |
