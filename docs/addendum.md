[← Back to index](index.md)

# Addendum: Running on a Shared Training Server

The original exercises (5, 6, 7) assume you have exclusive use of ports `8000` and `8501` on your own laptop. On a shared multi-user training box — like the one this build was actually run on, where several other students were running the same exercises concurrently — those ports are frequently already taken by someone else's session, and a stray API key can pick up invisible characters that break outbound calls in ways the original walkthrough doesn't anticipate. This page documents both gotchas and the fix that was added to the real [`/expenseflow`](../expenseflow) build.

## 1. Port collisions

**Symptom:** `uvicorn app.main:app --reload` or `streamlit run ui/app.py` fails with `[Errno 98] error while attempting to bind on address ... address already in use`, even though *you* haven't started anything yet.

**Cause:** on a shared server, ports 8000, 8001, 8501, 8503, and 8504 are common defaults for exactly the tools this course uses (Uvicorn, Streamlit), so collisions with other users are the norm, not the exception — unlike a personal laptop where you're the only process on the machine.

**Fix used in this build:** `expenseflow/run.sh` and `expenseflow/stop.sh` were added on top of the exercises. `run.sh`:

1. Asks the OS for two free ports (binding to port `0` and reading back what the kernel assigned), instead of hardcoding 8000/8501.
2. Starts the API on the first port, and polls `GET /health` until it responds before continuing.
3. Starts Streamlit on the second port with `API_BASE` set to the API's actual URL, and polls Streamlit's own `/_stcore/health` endpoint.
4. Prints both URLs once both are confirmed up.

```bash
cd expenseflow
./run.sh
# ExpenseFlow is running:
#   API docs:  http://127.0.0.1:<port>/docs
#   UI:        http://127.0.0.1:<port>
./stop.sh   # when done
```

If you're working on your own machine and ports 8000/8501 are free, the exercises' original fixed-port commands work fine as written — `run.sh` is a convenience for shared environments, not a replacement.

## 2. A stray `\r` in `ANTHROPIC_API_KEY`

**Symptom:** Exercise 6's `/reports/insights` endpoint always returns the safe fallback text, and the Uvicorn console logs `anthropic.APIConnectionError: Connection error.` even though the key looks correct and `pip show anthropic` is fine.

**Cause:** if the key was copied from a source that used Windows-style line endings (`\r\n`) — for example pasted from a `.env`-style value that passed through a Windows shell or file — the trailing `\r` becomes part of the key string. That `\r` is an illegal character in an HTTP header value, so the underlying HTTP client raises a connection error before the request is even sent. This is easy to miss because `echo $ANTHROPIC_API_KEY` in a terminal usually displays it identically either way.

**Fix used in this build:**

- When writing `.env`, strip the value first: `os.environ.get("ANTHROPIC_API_KEY", "").strip()`.
- In `app/insights.py`, defensively `.strip()` the key again when constructing the `anthropic.Anthropic()` client, so a bad `.env` value doesn't reintroduce the bug:

```python
api_key = (os.environ.get("ANTHROPIC_API_KEY") or "").strip()
client = anthropic.Anthropic(api_key=api_key)
```

**If you hit this yourself:** check for it directly rather than guessing —

```bash
python3 -c "import os; print(repr(os.environ.get('ANTHROPIC_API_KEY', '')[-5:]))"
```

If the output ends in `\r'` instead of a normal character, that's the bug.

## 3. Model names are course placeholders

**Symptom:** following Exercise 6 literally with `model="claude-sonnet-4-6"` (or the stretch goal's `claude-haiku-4-5`) fails, because those aren't real callable model ids.

**Cause:** the course material uses illustrative model names that don't correspond to anything the Anthropic API will actually resolve. This is a documentation convenience, not a build instruction — the exercise text was never meant to be typed in as a literal, permanent model id.

**Fix used in this build:** `app/insights.py` substitutes a real current model id, with a comment left in place for traceability:

```python
# Course material calls this "claude-sonnet-4-6"; using the real current model id
# so the call actually resolves.
MODEL = "claude-sonnet-5"
```

**If you hit this yourself:** whatever model name a course, blog post, or old prompt gives you, check it against the current model list before wiring it into code that will actually run — `/model` inside Claude Code, or the Anthropic API docs, are the source of truth, not a fixed string in a walkthrough.

---
[← Back to index](index.md)
