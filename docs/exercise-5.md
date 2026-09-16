[← Back to index](index.md)

# Exercise 5: The API Surface — FastAPI Endpoints

*Phase 2 · Develop*

| | |
|---|---|
| **Dev cycle** | Develop (API) |
| **CC features** | Build loop, running the live server, validating in the Swagger UI (`/docs`), pydantic schemas |
| **Time** | 40 min |
| **You produce** | A running FastAPI app with create / list / get / approve / reject endpoints |

## Objective

Stand up the API itself. You will generate pydantic schemas and routes, run the live server with Uvicorn, and validate every endpoint by hand in the auto-generated Swagger UI. This is the most satisfying exercise: by the end you have a clickable API.

## Walk-through

### 1. Generate request and response schemas

pydantic models define the API contract. Keep them separate from the ORM model so the wire format and the storage format can diverge cleanly.

**Type this prompt into Claude Code**
```
Create app/schemas.py with pydantic v2 models: ExpenseCreate (description, amount_minor,
currency, category, submitted_by) and ExpenseOut (all fields including id,
amount_base_minor, status, created_at). Amounts are integer minor units. Add field
validation: amount_minor must be positive, currency is a 3-letter code.
```

> **VALIDATE** `app/schemas.py` defines `ExpenseCreate` and `ExpenseOut` with the field validation described above.

![schemas.py diff](images/exercise-5/img_001.png)
![Field validation on amount_minor and currency](images/exercise-5/img_002.png)

### 2. Generate the routes and app entry point

Now the endpoints and the FastAPI app. Tell Claude to leave the FX conversion as a clearly-marked stub for now: `amount_base_minor` equals `amount_minor`. You will wire real conversion in Exercise 6.

**Type this prompt into Claude Code**
```
Create app/routes.py with an APIRouter and app/main.py with the FastAPI app that
includes the router and calls init_db on startup. Endpoints from ARCHITECTURE.md:
POST /expenses (create, status pending), GET /expenses (list, optional status and
category query filters), GET /expenses/{id} (404 if missing), POST
/expenses/{id}/approve, POST /expenses/{id}/reject. For now set amount_base_minor =
amount_minor with a TODO comment marking where FX conversion goes. Use the get_db
dependency.
```

> **VALIDATE** Read the diff across `app/main.py` and `app/routes.py`. The TODO marker for FX conversion is present. Approve / reject set status and return the updated expense. Approve the changes.

![routes.py diff](images/exercise-5/img_003.png)
![main.py diff](images/exercise-5/img_004.png)
![TODO marker for FX conversion](images/exercise-5/img_005.png)

### 3. Run the live server

Start Uvicorn with auto-reload. Leave this terminal running and open a second PowerShell tab for other commands.

**Run in terminal**
```
PS> python -m uvicorn app.main:app --reload
```

> **VALIDATE** The terminal shows "Uvicorn running on http://127.0.0.1:8000" and "Application startup complete". Any traceback here is your next prompt to Claude: paste it whole.

![Uvicorn running](images/exercise-5/img_006.png)

### 4. Validate in the Swagger UI

FastAPI auto-generates interactive docs. Open them in your browser and exercise the API by hand. No code needed: this is the demoable surface.

**Open in your browser**
```
http://127.0.0.1:8000/docs
```

> **VALIDATE** All five endpoints appear. `POST /expenses` with a sample body returns 200 and a JSON expense with status `pending` and an id. `GET /expenses` returns it in a list. `GET` on a missing id returns 404. `POST .../approve` flips status to `approved`.

![Swagger UI listing all endpoints](images/exercise-5/img_007.png)

### 5. Drive one full journey

Use "Try it out" in Swagger to run the whole user journey end to end: submit, list, approve, confirm. This is your 60-second demo from the course.

**Sample `POST /expenses` bodies**

Example #1 (2500.00 INR, stored as paise):
```json
{
  "description": "Team lunch",
  "submitted_by": "bob",
  "category": "meals",
  "amount_minor": 250000,
  "currency": "INR"
}
```

Example #2:
```json
{
  "description": "Flight to Bangalore",
  "submitted_by": "alice",
  "category": "travel",
  "amount_minor": 15000,
  "currency": "USD"
}
```

> **VALIDATE** Submit returns id `1`, status `pending`. Approve id `1` returns status `approved`. `GET /expenses?status=approved` returns exactly that expense. The core journey works.

![Submitting an expense](images/exercise-5/img_008.png)
![Approving an expense](images/exercise-5/img_009.png)
![Filtering by status](images/exercise-5/img_010.png)

## What success looks like

- Uvicorn serves the app and the Swagger UI lists all five endpoints.
- You ran the full submit → list → approve journey by hand without writing client code.
- The FX conversion is a clearly-marked TODO, deliberately deferred, not silently faked.

## Common pitfalls (Windows and macOS)

- Port 8000 in use? Add `--port 8001` to the uvicorn command and open `/docs` on that port.
- Auto-reload only watches code files. If you change `CLAUDE.md` or `.env`, restart the server manually.
- Keep the server terminal running. Run all other commands in a second terminal tab so you do not kill it.

## Stretch goal

Ask Claude to add a `GET /health` endpoint that returns status `ok` and the row count of expenses. Health checks are the first thing any deployment platform asks for.

---
[← Previous: Exercise 4](exercise-4.md) · [Back to index](index.md) · [Next: Exercise 6 →](exercise-6.md)
