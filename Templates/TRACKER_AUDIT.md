# Tracker Audit — after a scope-changing decision

Read this file only when triggered by rule 3 of APPEND_SYSTEM.md: a decision has changed what the pipeline produces or what the tool is.

## Why
A large decision does not just add an item to `TODO.md` or `DECISIONS.md`; it silently changes the meaning of items already written. A stale item does not read as stale — it reads as a clear instruction, and the next session will carry it out against the decision just made.

## What to check
Re-read the open items in `TODO.md` and `DECISIONS.md` asking **"does this still mean what it said before?"** — not "is this still true?". Most items stay true but stop being relevant, or quietly contradict the new decision.

## How
Do not just re-read the prose and declare it fine. Verify against the repository and the output tree, never from memory:
- Grep both trackers against each other: the same subject named in two items; an item that prescribes what another item still questions.
- Grep both trackers against disk: paths, filenames, or outputs the decision renamed or deleted.
- Update or remove every item the decision invalidated.

## Report
State what was checked and how. "I found nothing this pass" is weaker than "there is nothing" — do not present the first as the second. Small decisions usually invalidate nothing; scope-changing ones ripple.
