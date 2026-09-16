# ExpenseFlow — Technical Handoff

## What it does

ExpenseFlow lets a user submit an expense (description, amount, currency, category), view the list of submitted expenses, and approve or reject them. A separate endpoint asks Claude to summarise spending patterns across all stored expenses. A Streamlit UI provides a form and table on top of the API.

## How it works

- **`app/db.py`** creates a single SQLAlchemy `engine` against a local SQLite file (`expenseflow.db`), plus a `SessionLocal` factory and a `get_db()` FastAPI dependency that yields a session per request and always closes it. `init_db()` creates the schema on app startup (`app/main.py`'s startup event) — there is no separate migration step.
- **`app/models.py`** defines the single `Expense` ORM model. Money fields (`amount_minor`, `amount_base_minor`) are integers, never floats.
- **`app/schemas.py`** defines the pydantic v2 wire format (`ExpenseCreate` for input, `ExpenseOut` for output), kept deliberately separate from the ORM model.
- **`app/routes.py`** implements the CRUD + approval workflow, the `/reports/insights` endpoint, and `/health`. FX conversion is currently a stub (`amount_base_minor = amount_minor`) marked with a `TODO` — there is no real currency conversion yet.
- **`app/insights.py`** is the only external network dependency: it calls the Anthropic Messages API with a system prompt that forces strict JSON output (`{"summary": str, "bullets": [str, str, str]}`), validates the shape, retries once on any failure, and otherwise returns a hardcoded safe fallback. It never raises out of `generate_insight()`.
- **`ui/app.py`** is a single-file Streamlit app that talks to the API exclusively over HTTP via `httpx`, using the `API_BASE` environment variable (default `http://127.0.0.1:8000`). It has no direct database access and no server-side logic beyond formatting.

## What a deployment engineer needs to know

- **State lives in one SQLite file** (`expenseflow.db`), created automatically on first run. There is no connection pooling and no migration tool (e.g. Alembic) — schema changes today mean deleting and recreating the file, which loses data.
- **Secrets**: only `ANTHROPIC_API_KEY`, read from `.env` via `python-dotenv`. It must be set before `uvicorn` starts; `--reload` does not reliably pick up `.env` changes without a full restart.
- **No authentication or authorization** exists anywhere in the API. Anyone who can reach the port can submit, approve, or reject any expense.
- **Two processes to run**: the FastAPI app (`uvicorn`, default port 8000) and the Streamlit UI (default port 8501). They are independent OS processes sharing one SQLite file through the API — the UI never touches the database directly.
- **The `/reports/insights` endpoint makes an outbound network call** to `api.anthropic.com` on every request (no caching). If that network path is blocked or the key is invalid, the endpoint degrades gracefully to a fixed fallback response rather than failing the request — this is intentional, not a bug, but it means a broken key can go unnoticed if nobody checks server logs.
- **See `docs/PRODUCTION-GAP.md`** before treating this as anything beyond a local demo.
