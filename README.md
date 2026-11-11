# CV-BOT-IA

A chat-first CV: recruiters ask an AI assistant about Leonardo Mannanice's experience and get answers grounded in his CV, with a citation for every fact.

> **Work in progress.** The design is finished and the code is starting. The [roadmap](docs/ROADMAP.md) shows where it stands.

## Repository layout

| Folder | What lives there |
|---|---|
| `frontend/` | The site: React, Vite, TypeScript and Tailwind, built into static files for Hostinger (from step 3.3) |
| `backend/` | The API and the AI agents: Python, FastAPI and LangGraph, deployed to Railway |
| `content/` | Facts about Leonardo: profile, policies and case studies. Both the site and the assistant read them |
| `evals/` | Recruiter questions with the facts a good answer must contain, used to measure the assistant |
| `docs/` | The [roadmap](docs/ROADMAP.md), the [decisions](docs/DECISIONS.md), the [design](docs/DESIGN.md) and the [API contract](docs/API.md) |

Both apps live in one repository so that the API contract, the content and the code that uses them change together, in one reviewed pull request. Each app still deploys to its own host (ADR-002 and ADR-005 in [the decisions](docs/DECISIONS.md)).

## Run locally

Both apps use fixed ports away from the usual defaults (8001 instead of 8000, 5180 instead of 5173), so they can run next to other local projects.

### Backend

It needs [uv](https://docs.astral.sh/uv/), which installs the right Python by itself.

```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload --port 8001
```

Then open <http://localhost:8001/health>, or <http://localhost:8001/docs> for the interactive API docs.

Until the agents exist (Phase 5), `POST /chat` answers from scripts built from `content/` (ADR-022):

- questions about ServiME, his experience or his stack get their cards;
- a pasted job offer (400 characters or more) gets the job-fit report of the approved design;
- asking to contact him shows a sample summary to confirm, and `POST /contact` accepts it without sending anything;
- salary, start dates and unrelated topics get their redirect.

These messages force the cases a real model can't produce on demand. `mock: fail` and `mock: limit` also work as the message of `POST /contact`.

| Message | Answer |
|---|---|
| `mock: slow` | The usual answer, five times slower, to try the stop button |
| `mock: long` | Every role and project, with a citation each |
| `mock: fail` | A few words, then an `upstream_unavailable` error event |
| `mock: limit` | `429` with `Retry-After`, before any event |

### Frontend

It needs Node 26, the version in `frontend/.nvmrc`.

```bash
cd frontend
npm install
cp .env.example .env   # optional: a placeholder phone number shows the WhatsApp link
npm run dev
```

Then open <http://localhost:5180>. The chat talks to the backend, so keep it running too. The real phone number and the CV address reach the site only from the deploy's configuration (ADR-016).

### Content

Facts about Leonardo live in `content/` (ADR-015). The site reads a JSON copy of the profile, so after changing `content/profile.yaml`, export it again and commit both files (ADR-023):

```bash
cd backend
uv run python -m app.content.export
```

A test fails until the copy matches the profile.

### Evals

The assistant is scored on the recruiter questions in `evals/questions.yaml`. From `backend/` (needs the keys in `.env`; a run costs a few cents):

```bash
uv run python -m app.evals.run              # print the scores
uv run python -m app.evals.run --write      # also record the run in evals/RESULTS.md
uv run python -m app.evals.run --only servime,email-address
```

`evals/RESULTS.md` holds the latest run and the history; see ADR-031 for how a case is scored.

### Search index

The assistant retrieves from the case studies, which live as chunks in Postgres with pgvector (ADR-008, ADR-025). With `DATABASE_URL` and `OPENAI_API_KEY` in `backend/.env`, bring the index up to date after changing a case study:

```bash
cd backend
uv run python -m app.rag.ingest
```

It embeds only the sections that changed, so running it again costs nothing. CI does the same on every change to `content/case-studies/`, once both secrets exist in the repository settings.

### Commit hooks

[pre-commit](https://pre-commit.com) checks every commit before it enters the history. It formats and lints the files that changed, and blocks leaked secrets with gitleaks. When `content/` or `evals/` change, it also blocks phone numbers and email addresses that must not be published. Set it up once per clone, after installing both apps:

```bash
uv tool install pre-commit
pre-commit install
```

### Checks

The same commands CI runs:

```bash
cd backend
uv run ruff format --check . && uv run ruff check . && uv run mypy . && uv run pytest

cd ../frontend
npm run format:check && npm run lint && npm run typecheck && npm run test -- --run && npm run build
```
