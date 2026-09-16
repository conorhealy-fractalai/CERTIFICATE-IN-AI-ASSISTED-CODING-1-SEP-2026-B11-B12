[← Back to index](index.md)

# Exercise 9 (Bonus): Turtles All the Way Down — Recursive Self-Review

*Bonus — Reflect & Recurse*

| | |
|---|---|
| **Dev cycle** | Review |
| **CC features** | Plan mode, the Explore agent (or another subagent) for an uncontaminated second opinion, explicit judgment-call surfacing, the build loop applied to documentation as well as code |
| **Time** | 75 min — the most open-ended exercise in the course; budget more if you actually find things to fix |
| **You produce** | A findings list, at least one resolved judgment call, and a verified fix for every confirmed bug |

> **This exercise is not from the original workshop.** It's a bonus round documenting the process used to build the rest of `/docs` and `/expenseflow`: cross-check the training against the real code, get a genuinely independent adversarial review, resolve the ambiguous cases with a human instead of guessing, then plan and implement. This exercise teaches you to run that same process yourself.

## Objective

Every exercise so far ends with "and it works." This one adds the check most courses skip: go back and verify the work still matches what it claims about itself. AI-assisted code and docs drift — a comment stops being true, a documented decision never gets built, a temporary fix quietly becomes permanent scope — and that drift is invisible from inside the same context that produced it. This exercise is the concrete process for catching it: cross-check documentation against code, get a review from a context that never saw the original reasoning, separate confirmed bugs from real judgment calls instead of silently picking a side, then plan and verify the fix exactly the way you did in Exercises 3 through 6.

**Where this generalizes and where it doesn't:** Step 1 below (cross-checking a training doc against an implementation) only applies because this course happens to have both. Most projects you build with Claude Code won't have a parallel walkthrough to diff against — they'll have a `CLAUDE.md`, maybe a README, maybe ADRs. Steps 2 through 4 (independent review, judgment-call triage, plan-and-verify) have no such dependency and apply to anything you've built with Claude Code, with or without a training doc alongside it.

## Walk-through

### 1. Cross-check the training against the build

Start in plan mode. The first pass is mechanical: find places where the walkthrough and the real code disagree.

**Type this prompt into Claude Code**
```
Read every file under docs/ (the exercise walkthroughs) and every file under
expenseflow/ (the real implementation). Cross-check them against each other. Report,
as a flat list with file and line references: anywhere the docs describe a command,
file layout, endpoint, model name, or behavior that doesn't match what's actually in
the code; anywhere a documented "decision" isn't actually implemented; and anywhere
the code does something the docs never mention. Do not propose fixes yet — findings
only.
```

> **VALIDATE** You get a concrete, specific list — file paths and line numbers, not vague impressions. If Claude's findings are generic ("the docs could be clearer"), push back and ask for the exact sentence and the exact line of code that disagree with it.

### 2. Get an adversarial second opinion, deliberately uncontaminated

Here is the trap: if you ask the same conversation "was that work good?", it tends to agree with itself — it already committed to a framing while doing the work. Get the review from a context that never saw that framing: point Claude Code's Explore agent at it (the same feature from Exercise 3's stretch goal), or open a second, unrelated `claude` session against the same files, and tell it explicitly to argue against the choices made, not validate them.

**Type this prompt into Claude Code (in the fresh session/agent)**
```
Start fresh — do not assume anything a prior session decided was correct. Read docs/
and expenseflow/ cold. Give me a genuinely adversarial review: where is there
overengineering or scope creep in the code relative to a project whose own CLAUDE.md
says "PoC, not production"? Where has the training material stopped following its own
advice (check what exercise-2.md teaches about keeping CLAUDE.md tight — does the rest
of the course practice what it preaches)? Don't soften findings. Take a position on
whether this is close to ideal or not.
```

> **VALIDATE** The review names at least one specific line, file, or decision it disagrees with, and gives a concrete reason — not just an overall impression. If it agrees with everything on the first pass, that's a sign the context wasn't actually independent: ask it to argue the opposite side explicitly, or re-run it with even less framing.

### 3. Separate real bugs from genuine judgment calls

Not every finding is a bug. Some are legitimate design tensions with no obviously correct answer — and the worst thing you can do here is let Claude Code silently pick one and move on. When a finding is genuinely ambiguous, it should stop and ask you, the same way a careful human collaborator would.

**Type this prompt into Claude Code**
```
Of the findings from the last two reviews, which ones are unambiguous bugs (something
that contradicts its own stated intent), and which are judgment calls where reasonable
people could land differently? For the judgment calls, don't decide for me — lay out
the strongest version of each side and ask.
```

> **VALIDATE** Claude produces at least one real judgment call, not just a list of bugs. If everything gets bucketed as an obvious bug, ask "what's the strongest counter-argument to fixing that one?" — there is almost always one worth hearing before you act.

### 4. Plan the fix, then implement it for real

Back to the pattern from Exercise 3: force a plan before code changes, especially now that you're touching both the training text and the implementation it describes.

**Type this prompt into Claude Code**
```
Write a plan covering every confirmed bug and the judgment calls we just resolved.
Order it so code fixes land before any test or doc change that depends on them. Then
implement it, and after each change re-run the actual verification (pytest, a live
curl check, whatever applies) — don't mark something done because the diff looks
right.
```

> **VALIDATE** Every change is followed by a real check: `pytest` output, an actual HTTP response, a re-read of the edited file — not just "the edit succeeded." A plan that skips straight to "done" without evidence is the same failure mode Exercise 4 warned about: code that hasn't run is a guess.

## What success looks like

- A findings list from Step 1 with real file:line references — not impressions.
- At least one specific disagreement from the Step 2 review that you can quote, with a concrete reason attached.
- At least one judgment call from Step 3 that got resolved by you answering a question, not by Claude Code deciding silently.
- A written plan from Step 4, and for every item in it, a piece of verification evidence — a passing test run, an HTTP response, a re-read file — not just a completed-looking diff.

## Common pitfalls

- If you're reviewing your own work in the same conversation that did it: stop — that review is contaminated by construction. Get a fresh session or agent instead.
- If every finding from Step 3 gets marked "bug, fix it": pause and ask whether any are legitimate trade-offs where "we chose X, here's why" is the right answer, not a cop-out.
- If you're about to mark something done because "the diff matches the plan": don't. Run it — pytest, curl, a re-read of the file. A matching diff is not evidence anything works.

## Stretch goal

**Recurse.** Run Step 2's adversarial review again, fresh, against the changes you just made in Step 4 — treating your own output as the new prior work. A second pass that finds nothing above a documented, deliberately-deferred gap (a `PRODUCTION-GAP.md`-style entry) is a real result, not a failure to find something. Two or three passes total is normal. If a pass finds something *bigger* than the one before it, you introduced more problems than you fixed — stop and look at why before recursing again. If pass three is still finding the same class of issue as pass one, the problem is the design, not the surface: go back to plan mode.

Separately — or instead — point this whole process at a completely different project you or a teammate built with Claude Code. Step 1 won't apply (there's likely no separate training doc to check the code against), but Steps 2 through 4 do, unchanged. Notice which of your findings are project-specific and which are general Claude-Code-build smells — the second category is the actual transferable skill this course has been building toward since Exercise 1.

---
[← Previous: Exercise 8](exercise-8.md) · [Back to index](index.md)
