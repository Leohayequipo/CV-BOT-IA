# CV-BOT-IA

Chat-first CV for Leonardo Mannanice: recruiters ask an AI assistant about his experience and get grounded, cited answers. This is a public portfolio project, so code quality is part of the product.

- **Plan:** follow [docs/ROADMAP.md](docs/ROADMAP.md) one step at a time. Don't start a step before the previous one is done.
- **Decisions:** [docs/DECISIONS.md](docs/DECISIONS.md) records what was chosen and why. Don't add technology that isn't justified there.
- **Standards:** use the `quality-standards` skill (`.claude/skills/quality-standards/`) for any code, test, prompt, content or CI change.
- **Content is facts about a real person:** never invent or change anything in `content/` without Leonardo's confirmation.
- **Language:** repo artifacts in English; talk to Leonardo in Spanish.

## Stack

React + Vite + TypeScript + Tailwind (static, Hostinger) → FastAPI + LangGraph + Claude (Railway) → Supabase pgvector, Langfuse.
