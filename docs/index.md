# ExpenseFlow: A Claude Code Build Walkthrough

This is a markdown conversion of the "Certification in AI-Assisted Coding" workshop exercises. Across eight exercises you use **Claude Code** to design, build, and ship **ExpenseFlow** — a small expense submission and approval API with an AI-generated spending insight feature and a Streamlit front end. A ninth, bonus exercise then turns Claude Code on the course itself.

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

*Note: this course numbers phases 1, 2, and 4 — Phase 3 covers material outside this exercise set and isn't included here.*

## Bonus (not from the original workshop)

- [Exercise 9 — Turtles All the Way Down: Recursive Self-Review](exercise-9.md)

## What you end up with

| Piece | Built in |
|---|---|
| Project scaffold, Python venv, `CLAUDE.md` constitution | Exercise 2 |
| `docs/ARCHITECTURE.md` — agreed schema, endpoints, file layout | Exercise 3 (endpoint table extended in Exercises 5 and 6) |
| `app/db.py`, `app/models.py` — SQLAlchemy engine and `Expense` ORM model | Exercise 4 |
| `app/schemas.py`, `app/routes.py`, `app/main.py` — FastAPI CRUD + approval workflow (with a `/health` check and double-approval enforcement) | Exercise 5 |
| `tests/` — pytest suite covering CRUD, filters, 404s, and the double-approval 409s | Exercise 5 |
| `app/insights.py`, `GET /reports/insights` — Claude-powered spending insights | Exercise 6 |
| `ui/app.py` — Streamlit front end | Exercise 7 |
| `README.md`, `docs/HANDOFF.md`, `docs/adr/`, `docs/PRODUCTION-GAP.md` | Exercise 8 |
| A documented review-and-fix cycle applied to this course and its own implementation | Exercise 9 (recursive — see its own note on provenance) |

## Addendum

- [Gotchas Hit Building the Reference Implementation](addendum.md) — port-collision handling via `run.sh`/`stop.sh`, a real `ANTHROPIC_API_KEY` gotcha, and a note on the course's placeholder model names.

## Notes on this conversion

- Every "Type this prompt into Claude Code" block is presented as the prompt used in the workshop. For most exercises this is a verbatim transcription of the source `.docx`. Exercises 3 and 5 are the exception: their source `.docx` files had duplicated or corrupted text in places (Exercise 3 repeated a walkthrough sentence three times in a row; Exercise 5's sample request-body section was visibly truncated/garbled), and those sections were editorially reconstructed for this conversion rather than copied verbatim.
- `VALIDATE` call-outs describe what you should see if the step worked, and are the fastest way to tell a good AI-generated diff from a bad one.
- "Common pitfalls" are Windows/macOS-specific gotchas from the original material.
- Screenshots are the original workshop screenshots, carried over from the source `.docx` files.
- Exercise 5 has been extended beyond the original workshop material with a core testing step and a promoted `/health` step (see that exercise's own note); Exercise 6 gained a small cross-reference to the same change. This was a deliberate improvement made after building and reviewing the reference implementation, not a transcription of the source `.docx`.
- Exercise 9 is entirely new: it exists nowhere in the source `.docx` or slide decks. It documents, as a repeatable exercise, the review-and-fix process actually used to produce every "extended beyond the original workshop material" note on this page — including this bullet.
