# Git, CI/CD and deploy standards

The commit history is part of the portfolio: a reviewer should be able to read it like a changelog of the project.

## Branches

- `main` is always deployable and protected: changes land only through PRs with green CI.
- Branch names: `<type>/<phase>.<step>-<short-name>`, e.g. `feat/5.2-hybrid-retrieval`, `fix/4.5-autoscroll-jump`, `docs/0.3-decisions`.

## Commits (Conventional Commits)

```
<type>(<scope>): <imperative summary, ≤ 72 chars>

<why this change, if not obvious>
```

- Types: `feat`, `fix`, `test`, `refactor`, `docs`, `chore`, `ci`, `perf`, `style`.
- Scopes: `frontend`, `backend`, `agents`, `rag`, `content`, `evals`, `ci`, `docs`.
- One logical change per commit. Don't mix formatting with behaviour changes.

## Pull requests

Use `.github/pull_request_template.md`:

- **What & why:** one paragraph and a link to the roadmap step.
- **How to test:** commands or steps.
- **Screenshots/GIF** for any UI change (mobile + desktop).
- **Evals:** before/after scores if prompts, content or retrieval changed.
- **Checklist:** the Definition of Done from `SKILL.md`.

Merge with a merge commit (GitHub's default button) and merge stacked PRs in order. Steps are often prepared ahead as stacked branches, each starting from the previous one, and only a merge commit keeps the next branches valid; squash and rebase merges rewrite the commits they build on. PR titles follow the commit format above, since they appear in the history.

## CI (GitHub Actions)

`ci.yml` runs on every PR and push to `main`:

1. `backend` (since step 1.6): uv sync → ruff format check → ruff → mypy → pytest. The content tests run here, so a broken fact in `content/` fails CI.
2. `frontend` (step 3.5): npm ci → prettier check → oxlint → tsc → vitest → build
3. `security` (step 7.4): secret scanning (gitleaks) and dependency audit
4. `evals` (step 7.1, only when `backend/app/prompts`, `backend/app/agents`, `backend/app/rag` or `content/` change): run the eval suite and compare it with the thresholds

Don't put path filters on the whole workflow: once branch protection requires a check, a workflow that never runs leaves the PR waiting forever. To skip a job, use a job-level condition, which reports the job as skipped. Cache dependencies. Keep the whole pipeline under ~5 minutes.

## Deploy

- `deploy-frontend.yml`: on merge to `main` with frontend changes, build and upload `dist/` to Hostinger over FTPS. Credentials live in GitHub secrets.
- Backend: Railway deploys from `main` with backend changes. Health check on `/health`; a failed check keeps the previous version running.
- `ingest.yml`: on merge with `content/` changes, re-run ingestion against production.
- Every deploy is traceable: the backend exposes the git SHA in `/health`, and the frontend embeds it in a meta tag.

## Secrets

- Never in the repo, not even in examples. `.env.example` has keys with fake values only.
- Where secrets live: GitHub Actions secrets (deploy), Railway variables (runtime), and Leonardo's password manager (source of truth).
- pre-commit runs gitleaks locally. If a secret ever lands in a commit, rotate it immediately; rewriting history is not enough.
