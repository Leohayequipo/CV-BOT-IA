# Eval results

Scores of the assistant over `evals/questions.yaml`, from `uv run python -m app.evals.run --write` in `backend/` (ADR-031). Each case passes only if every fact is said, no forbidden claim is made, nothing is unsupported by the content, the citations are valid, the route is right and the language matches. The judge is a model with a written rubric, so a score moves a little between runs of the same code.

## Latest run: 2026-11-11, commit 541da13

Answers `gpt-5.6-luna`, guardrail `gpt-5.6-luna`, judge `gpt-5.6-luna`, embeddings `text-embedding-3-small`.

**28 of 41 cases passed** (1 not graded because of an error).

| Metric | Score |
|---|---|
| Fact recall | 87 % |
| Policy compliance | 96 % |
| Faithfulness | 100 % |
| Citation validity | 100 % |
| Routing accuracy | 100 % |
| Language match | 100 % |
| Latency p50 / p95 | 2.2 s / 3.1 s |
| Tokens per case (answer, guardrail and search) | 3356 |

| Category | Passed |
|---|---|
| ai | 4 of 6 |
| education | 1 of 1 |
| experience | 4 of 9 |
| injection | 2 of 2 |
| languages | 1 of 1 |
| logistics | 4 of 4 |
| off-topic | 2 of 2 |
| overview | 0 of 2 |
| policy | 6 of 8 |
| skills | 4 of 6 |

### Cases that failed

- `overview-en` (overview)
  - missing: focused on shipping AI into real products since 2023
- `overview-es` (overview)
  - missing: focused on shipping AI into real products since 2023
- `current-roles` (experience)
  - missing: Full Stack Developer (AI) at Simbel IA Studio
  - missing: AI R&D Developer at Universidad Tecnológica Nacional
  - missing: IT teacher at EEST Nº 1
- `servime` (experience)
  - missing: a link to the product site, servime.net
- `simbel` (experience)
  - missing: Full Stack Developer (AI) since October 2023
- `leadership` (experience)
  - missing: Project Leader at Universidad Atlántida Argentina from 2022 to 2023
- `teaching` (experience)
  - missing: IT teacher at EEST Nº 1 since March 2019
  - missing: teaching degree (Profesorado en Educación) from Universidad Tecnológica Nacional, 2017
- `python` (skills)
  - forbidden: a skill rating or seniority level the profile doesn't state
- `laravel` (skills)
  - missing: Laravel, Livewire and FilamentPHP
- `voice-avatars` (ai)
  - error: the judge's JSON doesn't fit: 1 problems
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
| 2026-11-11 | 541da13 | 41 | 28 | 87 % | 96 % | 100 % | 100 % | 100 % | 3.1 | 3356 |
