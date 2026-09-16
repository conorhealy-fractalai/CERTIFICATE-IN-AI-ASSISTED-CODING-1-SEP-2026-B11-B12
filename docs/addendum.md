[← Back to index](index.md)

# Addendum: Gotchas Hit Building the Reference Implementation

Three things the exercises don't anticipate, found while building the real [`/expenseflow`](../expenseflow) implementation. If you want to learn the process that surfaced these — and run it yourself — see [Exercise 9](exercise-9.md).

## 1. Port collisions (shared machines)

The original exercises (5, 6, 7) assume exclusive use of ports `8000` and `8501`. On a shared multi-user training box — several other students running the same exercises concurrently — those ports are frequently already taken, and `uvicorn`/`streamlit` fail with `[Errno 98] address already in use` even though *you* haven't started anything.

**Fix used in this build:** `expenseflow/run.sh` / `stop.sh` ask the OS for two free ports instead of hardcoding 8000/8501, start the API, poll `GET /health` until it's up, start Streamlit on the second port with `API_BASE` pointed at the first, poll its `/_stcore/health`, then print both URLs:

```bash
cd expenseflow
./run.sh
# ExpenseFlow is running:
#   API docs:  http://127.0.0.1:<port>/docs
#   UI:        http://127.0.0.1:<port>
./stop.sh   # when done
```

If you're on your own machine with 8000/8501 free, the exercises' original fixed-port commands work fine as written — `run.sh` is a convenience for shared environments, not a replacement.

## 2. A stray `\r` in `ANTHROPIC_API_KEY`

If a key passes through a Windows-style line ending (`\r\n`) somewhere before landing in `.env`, the trailing `\r` becomes part of the key string — an illegal HTTP header character, so every call fails with `anthropic.APIConnectionError: Connection error.` even though the key "looks" right. Fix: strip it — `(os.environ.get("ANTHROPIC_API_KEY") or "").strip()` — both when writing `.env` and again in `app/insights.py` before constructing the client. Check for it directly with `python3 -c "import os; print(repr(os.environ.get('ANTHROPIC_API_KEY', '')[-5:]))"`; if it ends in `\r'`, that's the bug.

## 3. Model names in the course text are placeholders

`claude-sonnet-4-6` and `claude-haiku-4-5` (Exercise 6) are illustrative, not real callable model ids — using them literally raises a 404. `app/insights.py` substitutes a real current model id with a comment for traceability. Whatever model name a course, blog post, or old prompt gives you, check it against `/model` inside Claude Code or the Anthropic API docs before wiring it into code that will actually run.

---
[← Back to index](index.md)
