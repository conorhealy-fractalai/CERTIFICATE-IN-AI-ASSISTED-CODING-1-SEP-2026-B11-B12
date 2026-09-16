# ExpenseFlow

A small expense submission and approval API, built as a proof of concept. One user journey: submit an expense, normalise it to a base currency, approve or reject it. Includes an AI-generated spending insights endpoint (Claude) and a Streamlit front end.

This is a PoC, not a production system — see [`docs/PRODUCTION-GAP.md`](docs/PRODUCTION-GAP.md) for what's missing before it could ship for real.

## Stack

- Python 3.10+, FastAPI, Uvicorn
- SQLAlchemy ORM on SQLite (`expenseflow.db`)
- pydantic v2 for request/response models
- `anthropic` SDK for AI-generated insights
- Streamlit for the UI
- pytest for tests

## Setup

### Windows (PowerShell)

```powershell
cd expenseflow
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### macOS / Linux

```bash
cd expenseflow
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configure `.env`

Create a `.env` file in the project root (never commit it — it's already in `.gitignore`):

```
ANTHROPIC_API_KEY=sk-ant-your-real-key-here
```

`GET /reports/insights` will return a safe fallback message if this key is missing or invalid.

## Run

Start the API:

```bash
python -m uvicorn app.main:app --reload
```

This creates `expenseflow.db` and its schema automatically on startup, and serves interactive API docs at `http://127.0.0.1:8000/docs`.

In a second terminal (venv activated), start the UI:

```bash
streamlit run ui/app.py
```

Open `http://localhost:8501`. The UI reads its API location from the `API_BASE` environment variable, defaulting to `http://127.0.0.1:8000`.

## Test

```bash
python -m pytest -q
```

## Endpoint reference

| Method | Path | Description |
|---|---|---|
| `POST` | `/expenses` | Submit a new expense. Body: `description`, `amount_minor` (int, >0), `currency` (3-letter code), `category`, `submitted_by`. Returns the created expense with `status="pending"`. |
| `GET` | `/expenses` | List expenses. Optional query params: `status`, `category`. |
| `GET` | `/expenses/{id}` | Get one expense by id. 404 if it doesn't exist. |
| `POST` | `/expenses/{id}/approve` | Set an expense's status to `approved`. |
| `POST` | `/expenses/{id}/reject` | Set an expense's status to `rejected`. |
| `GET` | `/reports/insights` | AI-generated spending summary: `{"summary": str, "bullets": [str, str, str]}`. Falls back to a safe default if the AI call fails. |
| `GET` | `/health` | `{"status": "ok", "count": <number of expenses>}`. |

## Money handling

Amounts are always stored and transmitted as **integer minor units** (e.g. paise, cents) — never floats — to avoid rounding errors. See [`docs/adr/0001-money-as-integer-minor-units.md`](docs/adr/0001-money-as-integer-minor-units.md) for the reasoning. The UI divides by 100 for display only.

## Project docs

- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — schema, endpoints, file layout, edge-case decisions
- [`docs/HANDOFF.md`](docs/HANDOFF.md) — what a deployment engineer needs to know
- [`docs/PRODUCTION-GAP.md`](docs/PRODUCTION-GAP.md) — honest gap audit against a production bar
- [`docs/adr/0001-money-as-integer-minor-units.md`](docs/adr/0001-money-as-integer-minor-units.md) — ADR on money representation

This project was built by directing Claude Code through an 8-exercise workshop; see [`/docs`](../docs/index.md) at the repository root for the full walkthrough.
