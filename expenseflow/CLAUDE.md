# ExpenseFlow API

## What this is
A small expense submission and approval API. PoC, not production.
One user journey: submit an expense, convert it to a base currency, approve or reject it.

## Stack
- Python 3.10, FastAPI, Uvicorn
- SQLAlchemy ORM on SQLite (file: expenseflow.db) for the PoC
- httpx — currently only used by ui/app.py to call the FastAPI backend over HTTP. There is no real FX-rate call yet (FX conversion is a stub, see app/routes.py); wiring a real FX provider via httpx is future work, not built.
- pydantic v2 for request and response models
- pytest for tests
- anthropic SDK for the insights endpoint
- Streamlit for the UI (ui/app.py)

## Conventions
- Layout: app/main.py, app/db.py, app/models.py, app/schemas.py, app/routes.py, app/insights.py, ui/app.py
- Type hints on every function. Docstrings on every endpoint.
- Money is stored as integer minor units (paise / cents), never float.
- Base currency is INR. All amounts are normalised to base on write.
- Never hardcode secrets. Read them from environment variables via python-dotenv.

## Run and test
- Run API:      python -m uvicorn app.main:app --reload
- Run UI:       streamlit run ui/app.py
- Test:         python -m pytest -q

## Do not touch
- Do not edit .venv, .git, or expenseflow.db directly.
- Do not add new third-party dependencies without telling me first.
- Do not invent endpoints that are not in the brief.
