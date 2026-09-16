[← Back to index](index.md)

# Exercise 7: Put a Face On It — A Streamlit UI

*Phase 4 · Extend, Automate & Ship*

| | |
|---|---|
| **Dev cycle** | Ship (stakeholder demo) |
| **CC features** | Streamlit UI built by Claude Code, calling the running FastAPI with httpx, running two servers together |
| **Time** | 40 min |
| **You produce** | `ui/app.py`: a Streamlit front end to submit, list, and get AI insights on expenses |

## Objective

An API is invisible to the people who sign off on it. As a capstone you will put a face on ExpenseFlow: a small Streamlit app that talks to your running FastAPI over httpx. You build it the same way you built everything else, by directing Claude Code, then you run the two servers side by side. This is the demo you show a stakeholder.

## Walk-through

### 1. Install Streamlit

Add Streamlit to the active venv. Identical on every OS while the venv is active.

**Run in terminal**
```
PS> pip install streamlit
```

> **VALIDATE** `streamlit --version` prints a version number.

![Installing Streamlit](images/exercise-7/img_001.png)

### 2. Have Claude Code build the UI

Ask for a single-file app that calls your API. The UI talks to the backend over HTTP, so it stays cleanly decoupled.

**Type this prompt into Claude Code**
```
Create ui/app.py: a Streamlit app that talks to the ExpenseFlow API using httpx. Read
the base URL from an environment variable API_BASE defaulting to
http://127.0.0.1:8000. Provide three things: a form to submit a new expense (amount,
currency, category, description) that POSTs to the API; a section that lists existing
expenses in a table by calling the API; and a button labelled Generate insights that
calls GET /reports/insights and renders the summary plus the three bullets. Handle
connection errors with a friendly message instead of a stack trace. Add a short module
docstring.
```

> **VALIDATE** `ui/app.py` exists and uses httpx, an `st.form` for submission, a table for the list, and reads `API_BASE` from the environment with a sensible default.

### 3. Run both servers

Keep FastAPI running in your first terminal. Open a second terminal, activate the venv there too, and start Streamlit. Activation is the one command that differs by platform.

Terminal 1 keeps running:
```
python -m uvicorn app.main:app --reload
```

**Windows · PowerShell**
```
PS> .\.venv\Scripts\Activate.ps1
PS> streamlit run ui/app.py
```

**macOS / Linux · bash or zsh**
```bash
$ source .venv/bin/activate
$ streamlit run ui/app.py
```

**Open in your browser (same URL on every OS)**
```
http://localhost:8501
```

> **VALIDATE** The Streamlit page loads. Submitting the form adds an expense that appears in the list. Generate insights shows the summary and three bullets from your Exercise 6 endpoint.

![Streamlit app running](images/exercise-7/img_002.png)

### 4. Prove the round trip

Show that the UI and the API are two faces of one backend, not separate stores.

**Open the API docs in a third browser tab**
```
http://127.0.0.1:8000/docs
```

> **VALIDATE** An expense you typed into Streamlit also appears when you list expenses from the API docs. One backend, two surfaces, one source of truth.

![Expense submitted via Streamlit](images/exercise-7/img_003.png)
![Same expense visible in Swagger](images/exercise-7/img_004.png)
![Round trip confirmed, part 1](images/exercise-7/img_005.png)
![Round trip confirmed, part 2](images/exercise-7/img_006.png)

### 5. Make it demo-ready

Iterate on polish through Claude Code, just as you iterated on the prompt in Exercise 6.

**Type this prompt into Claude Code**
```
Improve ui/app.py: add a title and a short caption, format amounts from integer minor
units into rupees with two decimals for display only, label the status (pending,
approved, rejected) clearly, and disable the submit button while a request is in
flight. Keep everything in the one file.
```

> **VALIDATE** Amounts render as currency rather than raw paise, status is readable, and the form cannot be double-submitted. The UI now looks like something you would put in front of a stakeholder.

![Polished UI with currency formatting](images/exercise-7/img_007.png)
![Status labels and disabled submit button](images/exercise-7/img_008.png)

## What success looks like

- You built a working UI for ExpenseFlow entirely by directing Claude Code, and it talks to your real running API.
- You can run the full stack locally: FastAPI in one terminal, Streamlit in another, sharing one database.
- You understand why the UI reads `API_BASE` from the environment: the same front end could in principle point at a different backend (e.g. a Postgres-backed API) with no code change — though no such backend is built or validated in this repo; see the stretch goal.

## Common pitfalls (Windows and macOS)

- `streamlit not found` in the second terminal almost always means the venv was not activated there. Activate it first, then run streamlit.
- Port already in use: if 8501 or 8000 is taken, stop the old process, or start Streamlit with `--server.port` on a free port. On a shared machine, see the [addendum](addendum.md) for a `run.sh` script that picks free ports for both servers automatically and wires `API_BASE` for you.
- There is no browser CORS problem here because Streamlit calls the API server-side through httpx, not from the browser. Do not add CORS hacks you do not need.
- Displaying money: divide integer minor units by 100 for display only. Never store or send floats; the integer remains the source of truth.

## Stretch goal

Ask Claude to add a `requirements.txt` (from `pip freeze`) and a README section explaining how to launch both servers from a clean clone, so a teammate can run the whole demo. Then — as a hypothetical, not something to actually build here — consider what it would take to point `API_BASE` at a Postgres-backed API instead; `docs/PRODUCTION-GAP.md` lists that migration as unbuilt future work, and the UI's dependence only on `API_BASE` and the HTTP contract is exactly what would make swapping the backend a non-event for `ui/app.py`.

---
[← Previous: Exercise 6](exercise-6.md) · [Back to index](index.md) · [Next: Exercise 8 →](exercise-8.md)
