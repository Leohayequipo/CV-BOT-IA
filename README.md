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
| `docs/` | The [roadmap](docs/ROADMAP.md), the [decisions](docs/DECISIONS.md) and the [design](docs/DESIGN.md) |

Both apps live in one repository so that the API contract, the content and the code that uses them change together, in one reviewed pull request. Each app still deploys to its own host (ADR-002 and ADR-005 in [the decisions](docs/DECISIONS.md)).
