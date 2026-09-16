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
| `POST` | `/expenses/{id}/approve` | — | `ExpenseOut` with `status="approved"` |
| `POST` | `/expenses/{id}/reject` | — | `ExpenseOut` with `status="rejected"` |
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
2. **Double approval / conflicting state transitions.** Nothing stops calling `/approve` on an already-rejected expense in the PoC. Decision: this is documented as an explicit known gap rather than silently allowed or silently blocked — the approve/reject handlers set status unconditionally. A production version would reject a transition out of a terminal state (`approved`/`rejected` → `approved`) with a 409.
3. **AI insight reliability.** `GET /reports/insights` depends on an external LLM call that can time out, return malformed output, or hit a rate limit. Decision: `generate_insight` requests strict JSON, validates the shape, retries once on failure, and falls back to a safe default object rather than ever raising through to the client (see Exercise 6).
