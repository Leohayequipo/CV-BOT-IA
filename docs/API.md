# API

The contract between the site and the backend. The mock server (step 4.3) and the real backend (Phase 5) both follow it, and the frontend is built and tested against it, so a change here is a change to both apps in the same pull request.

**Contents:** [Conventions](#conventions) · [`POST /chat`](#post-chat) · [Events](#events) · [Cards](#cards) · [`POST /contact`](#post-contact) · [`GET /health`](#get-health) · [Errors](#errors)

## Conventions

- JSON everywhere, with `snake_case` field names.
- Production: `https://api.<domain>`; locally: `http://localhost:8001`. CORS allows only the site's origin (`http://localhost:5180` in development).
- The server keeps no conversation state. The site sends the recent history with each question, so any backend instance can answer it.
- `session_id` is a random UUID the site creates when the page loads and keeps in memory. It's used only for rate limiting, never to identify a person.
- Limits live in the backend configuration. Their defaults: a message of up to 6,000 characters (a pasted job offer fits) and a history of up to 20 messages.

## `POST /chat`

Asks a question and streams the answer as [Server-Sent Events](https://html.spec.whatwg.org/multipage/server-sent-events.html).

```json
{
  "message": "What AI projects has he built?",
  "history": [
    { "role": "assistant", "content": "Hi, I'm Leonardo's assistant…" },
    { "role": "user", "content": "Can he work in the EU?" },
    { "role": "assistant", "content": "Yes. He holds Italian citizenship… [1]" }
  ],
  "locale": "en",
  "session_id": "6f1c2d8e-4b7a-4c5e-9d3f-2a1b0c9e8d7f"
}
```

| Field | Type | Rules |
|---|---|---|
| `message` | string | 1 to 6,000 characters after trimming |
| `history` | array of `{role, content}` | Oldest first; `role` is `user` or `assistant`; up to 20 items |
| `locale` | `"en"` or `"es"` | The interface language. Suggestions and error messages use it; the answer follows the language of the question |
| `session_id` | UUID | Created by the site on page load |

A valid request answers `200` with `Content-Type: text/event-stream`. Problems found before the stream starts answer with a normal [error](#errors) instead: `422` for an invalid body, `429` for the rate limit.

The site sends the request with `fetch` and reads the body as a stream, since `EventSource` can't send a POST. To stop an answer, it aborts the request, and the server stops generating.

## Events

Each event has a name and a JSON payload:

```
event: token
data: {"text": "Leonardo built "}

```

| Event | Payload | Meaning |
|---|---|---|
| `node` | `{"node": "guardrail"}` | A step of the graph started: `guardrail`, `supervisor`, `profile`, `job_fit` or `contact`. The cover graph lights up the path (ADR-020) |
| `token` | `{"text": "…"}` | The next piece of the answer, as Markdown. Citations appear in it as `[1]`, `[2]`… |
| `citation` | `{"id": 1, "label": "UTN · AI R&D", "source": "case-studies/rag-document-assistant.md", "section": "Results"}` | A source the answer cites. It always arrives before the first `[id]` that refers to it |
| `card` | `{"type": "project", "data": {…}}` | A card to show after the text; see [Cards](#cards) |
| `done` | `{"suggestions": ["…", "…"]}` | The answer is complete; `suggestions` holds the next questions to offer (may be empty) |
| `error` | `{"code": "upstream_unavailable", "message": "…", "retry_after": null}` | The answer failed partway; see [Errors](#errors) |

**Order.** Zero or more `node` events come first. Then `token` and `citation` events interleave, and `card` events follow the text. Every stream ends with exactly one `done` or one `error`, and then the server closes it.

A citation's `label` is what the sources row shows; `source` and `section` point to the file and the heading the fact came from, and the backend only cites chunks it actually retrieved. A `[n]` marker with no matching citation is shown as plain text.

## Cards

Every card has a `type` and a `data` object. Text inside cards may carry `[n]` citation markers too.

**`project`**

```json
{
  "name": "ServiME",
  "summary": "Digital menu SaaS with an AI chat",
  "role": "Lead developer",
  "period": "Aug 2026 – present",
  "highlight": "20% faster service at Azopardo Café Bar",
  "stack": ["Laravel", "Blade", "Tailwind CSS", "MySQL", "OpenAI", "Gemini"],
  "url": "https://servime.net",
  "brand": "servime"
}
```

`url` and `brand` may be `null`. `brand` selects the project's own colours for its band and logo tile (see `DESIGN.md`); without one, the card uses the teal set.

**`timeline`**

```json
{ "items": [{ "role": "Lead developer", "company": "ServiME", "period": "Aug 2026 – present", "initials": "SM" }] }
```

Newest first.

**`skills`**

```json
{ "groups": [{ "label": "LLMs and AI", "items": ["OpenAI", "Anthropic Claude", "Gemini", "RAG", "LangGraph"] }] }
```

**`job_fit`**

```json
{
  "title": "AI Engineer · remote in the EU",
  "requirements": [
    { "requirement": "Python and FastAPI", "status": "met", "evidence": "Python backend with FastAPI at UTN [1]" },
    { "requirement": "English C1", "status": "partial", "evidence": "B1, with daily conversation practice [3]" },
    { "requirement": "AWS", "status": "missing", "evidence": "Not in his CV" }
  ]
}
```

`status` is `met`, `partial` or `missing`. The site counts the totals for the summary line and the bar, so they can't disagree with the rows.

**`contact_summary`**

```json
{ "name": "Laura Gómez", "company": "Example Ltd", "email": "laura.gomez@example.com", "message": "I'd like to arrange an interview…" }
```

The details the contact agent collected, shown for confirmation. Nothing is sent until the visitor confirms with [`POST /contact`](#post-contact).

## `POST /contact`

Sends the confirmed message to Leonardo by email. It's a separate request, so the side effect happens only on the visitor's explicit confirmation, never as part of a model's answer.

```json
{
  "name": "Laura Gómez",
  "company": "Example Ltd",
  "email": "laura.gomez@example.com",
  "message": "I'd like to arrange an interview for an AI Engineer role next week.",
  "session_id": "6f1c2d8e-4b7a-4c5e-9d3f-2a1b0c9e8d7f"
}
```

| Field | Rules |
|---|---|
| `name` | 1 to 100 characters |
| `company` | Up to 100 characters; may be empty |
| `email` | A valid email address |
| `message` | 1 to 2,000 characters |
| `session_id` | The chat's UUID |

It answers `202` with `{"sent_at": "2026-10-31T10:32:00Z"}`, and the site then shows the "message sent" card. It has its own, stricter rate limit.

## `GET /health`

`200` with `{"status": "ok", "git_sha": "abc1234"}`. Railway calls it before a new version takes traffic, and the SHA shows which commit is live.

## Errors

Outside a stream, every error answers with its HTTP status and one shape:

```json
{ "error": { "code": "rate_limited", "message": "You've reached the question limit for now. Try again in a few minutes." } }
```

Inside a stream, the same `code` and `message` arrive in an `error` event, followed by the end of the stream. `message` is written for the visitor, in the request's `locale` (English when the body can't be read); it never contains stack traces, provider messages or prompts.

| Code | HTTP | When | What the site shows |
|---|---|---|---|
| `invalid_request` | 422 | The body breaks the rules above | The error notice; the site checks its input before sending, so this points to a bug |
| `message_too_long` | 422 | The message is over the limit | A note to shorten it |
| `rate_limited` | 429 | Too many questions from the session or the IP | The question-limit notice. The `Retry-After` header (or `retry_after` in the event) gives the seconds to wait |
| `upstream_unavailable` | 503 or event | The model provider failed or timed out after retries | The error notice with "Retry" |
| `internal_error` | 500 or event | Anything unexpected | The error notice with "Retry" |

A network failure (no response at all) shows the same error notice; the site tells it apart from the codes above only to decide the wording.
