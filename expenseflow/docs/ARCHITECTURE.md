# ExpenseFlow Architecture

Agreed design for the ExpenseFlow proof of concept, per `CLAUDE.md`. This is the source of truth for the build.

## 1. Schema: `expenses` table

| Column | Type | Why |
|---|---|---|
| `id` | INTEGER PRIMARY KEY | Row identity, referenced by approve/reject. |
| `description` | TEXT NOT NULL | Human-readable line item shown in the UI and reports. |
| `submitted_by` | TEXT NOT NULL | Who filed the expense; needed for any future audit trail. |
| `category` | TEXT NOT NULL | Groups spend for the insights feature and filtering. |
| `amount_minor` | INTEGER NOT NULL | The original amount in integer minor units (paise/cents) as submitted, in `currency`. Integers avoid float rounding errors in money. |
| `currency` | TEXT NOT NULL | 3-letter ISO code of the amount as submitted. Needed because not every expense is filed in the base currency. |
| `amount_base_minor` | INTEGER NOT NULL | `amount_minor` converted to the base currency (INR), also integer minor units. Kept separate from `amount_minor` so the original submission is never lossily overwritten and every report can sum in one currency. |
| `status` | TEXT NOT NULL DEFAULT `'pending'` | One of `pending`, `approved`, `rejected`. Drives the approval workflow. |
| `created_at` | DATETIME NOT NULL DEFAULT now | Audit/ordering; also what "recent spend" reports would filter on. |

## 2. Endpoints

| Method | Path | Request body | Response |
|---|---|---|---|
| `POST` | `/expenses` | `ExpenseCreate` (`description`, `amount_minor`, `currency`, `category`, `submitted_by`) | `ExpenseOut`, status `pending`, `amount_base_minor` computed |
| `GET` | `/expenses` | — (query params `status`, `category` optional) | `list[ExpenseOut]` |
| `GET` | `/expenses/{id}` | — | `ExpenseOut`, or 404 if missing |
| `POST` | `/expenses/{id}/approve` | — | `ExpenseOut` with `status="approved"` (409 if already `approved`/`rejected`) |
| `POST` | `/expenses/{id}/reject` | — | `ExpenseOut` with `status="rejected"` (409 if already `approved`/`rejected`) |
| `GET` | `/reports/insights` | — | `{"summary": str, "bullets": [str, str, str]}` — Claude-generated summary of stored expenses |
| `GET` | `/health` | — | `{"status": "ok", "count": int}` |

## 3. File layout

```
expenseflow/
├── CLAUDE.md
├── README.md
├── requirements.txt
├── run.sh / stop.sh       # start/stop API + UI on free local ports (see ../../docs/addendum.md)
├── .env                  # ANTHROPIC_API_KEY (never committed)
├── expenseflow.db         # SQLite file (never committed)
├── app/
│   ├── __init__.py
│   ├── db.py              # engine, SessionLocal, Base, get_db, init_db
│   ├── models.py           # Expense ORM model
│   ├── schemas.py           # ExpenseCreate / ExpenseOut pydantic v2 models
│   ├── routes.py           # APIRouter: CRUD + approve/reject + insights + health
│   ├── main.py             # FastAPI() app, includes router, calls init_db on startup
│   └── insights.py          # generate_insight(): calls the Anthropic Messages API
├── ui/
│   └── app.py              # Streamlit front end, calls the API over httpx
└── docs/
    ├── ARCHITECTURE.md      # this file
    ├── HANDOFF.md
    ├── PRODUCTION-GAP.md
    └── adr/
        └── 0001-money-as-integer-minor-units.md
```

## 4. Edge cases and decisions

1. **FX conversion failure.** The FX lookup is an external dependency (httpx call in a real build) and can fail or be slow. Decision: FX conversion is a clearly-marked stub in Exercise 5 (`amount_base_minor = amount_minor`, `TODO` comment). In a real production build this would need a cached last-known rate and a fallback so expense submission never blocks on a flaky external FX API.
2. **Double approval / conflicting state transitions.** Decision (Exercise 3): a transition out of a terminal state (`approved`/`rejected` → `approved` or `rejected`) must be rejected, not silently applied. This is enforced in `app/routes.py`: both `/approve` and `/reject` check the expense's current status first and return `409` if it is already `approved` or `rejected`.
3. **AI insight reliability.** `GET /reports/insights` depends on an external LLM call that can time out, return malformed output, or hit a rate limit. Decision: `generate_insight` requests strict JSON, validates the shape, retries once on failure, and falls back to a safe default object rather than ever raising through to the client (see Exercise 6). In practice, the model sometimes wraps its JSON in a ` ```json ` code fence despite being told not to — `_strip_code_fence()` strips that defensively before parsing, since the system prompt alone isn't reliable enough to skip this check.
4. **Multi-currency insight summarization.** `amount_base_minor` is currently an uncorrected copy of `amount_minor` (see edge case 1 — FX conversion is a stub), so a mixed-currency dataset is not actually normalised to one unit yet. Decision: `/reports/insights` passes each expense's original `currency` alongside its amount in the summary text, and the system prompt instructs the model not to sum or average across differing currencies without explicitly noting the mixture.
