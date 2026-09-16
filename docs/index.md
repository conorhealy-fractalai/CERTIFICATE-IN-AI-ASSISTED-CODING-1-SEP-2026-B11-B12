# ExpenseFlow: A Claude Code Build Walkthrough

This is a markdown conversion of the "Certification in AI-Assisted Coding" workshop exercises. Across eight exercises you use **Claude Code** to design, build, and ship **ExpenseFlow** — a small expense submission and approval API with an AI-generated spending insight feature and a Streamlit front end.

The original source material is the set of `Exercise *.docx` files and `S*_FAA_Claude - Final.pdf` slide decks in the repository root. These pages present the walkthrough portions (steps, commands, prompts, validation checks, screenshots) as plain markdown so they can be read on GitHub or served as a GitHub Pages site.

A working implementation built by following these exact steps lives in [`/expenseflow`](../expenseflow) at the root of this repository.

## Phase 1 · Design & Orient

- [Exercise 1 — First Contact: Orient Inside Claude Code](exercise-1.md)
- [Exercise 2 — Project Genesis: `/init` and the CLAUDE.md Constitution](exercise-2.md)
- [Exercise 3 — Architect First: Plan Mode and the Explore Agent](exercise-3.md)

## Phase 2 · Develop

- [Exercise 4 — The Data Layer: SQL Schema and ORM Models](exercise-4.md)
- [Exercise 5 — The API Surface: FastAPI Endpoints](exercise-5.md)
- [Exercise 6 — Insights with the Claude API](exercise-6.md)

## Phase 4 · Extend, Automate & Ship

- [Exercise 7 — Put a Face On It: A Streamlit UI](exercise-7.md)
- [Exercise 8 — Document and Ship](exercise-8.md)

## What you end up with

| Piece | Built in |
|---|---|
| Project scaffold, Python venv, `CLAUDE.md` constitution | Exercise 2 |
| `docs/ARCHITECTURE.md` — agreed schema, endpoints, file layout | Exercise 3 |
| `app/db.py`, `app/models.py` — SQLAlchemy engine and `Expense` ORM model | Exercise 4 |
| `app/schemas.py`, `app/routes.py`, `app/main.py` — FastAPI CRUD + approval workflow | Exercise 5 |
| `app/insights.py`, `GET /reports/insights` — Claude-powered spending insights | Exercise 6 |
| `ui/app.py` — Streamlit front end | Exercise 7 |
| `README.md`, `docs/HANDOFF.md`, `docs/adr/`, `docs/PRODUCTION-GAP.md` | Exercise 8 |

## Addendum

- [Running on a Shared Training Server](addendum.md) — port-collision handling via `run.sh`/`stop.sh`, and a real `ANTHROPIC_API_KEY` gotcha hit and fixed during this build.

## Notes on this conversion

- Every "Type this prompt into Claude Code" block is the literal prompt used in the workshop, preserved verbatim so you can replay the build yourself.
- `VALIDATE` call-outs describe what you should see if the step worked, and are the fastest way to tell a good AI-generated diff from a bad one.
- "Common pitfalls" are Windows/macOS-specific gotchas from the original material.
- Screenshots are the original workshop screenshots, carried over from the source `.docx` files.
