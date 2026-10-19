---
name: refactor-python
description: Full post-development cleanup pass over a Python codebase — graph sync, dead and stale code removal, numpydoc docstring sweep — behind an interactive approval gate. Use when the user asks for a cleanup, refactor pass, dead-code purge or docstring sweep of an existing project. For writing or editing individual code, use writing-python instead.
---

# Refactor pass

This pass applies the standards in `writing-python`. Read these at the moment named:

- Before scanning or rewriting any docstring: '/path/to/.pi/agent/skills/writing-python/references/docstrings.md`
- Before Phase 4: `/path/to/.pi/agent/skills/writing-python/references/procedures.md` (refactoring section)
- Before reporting done: `/path/to/.pi/agent/skills/writing-python/references/checklist.md`

## Phase 1 — Sync the graph

Before any analysis, run `/graphify <project root> --update --mode deep`.

## Phase 2 — Scan

Read the `graphify-output` map. Identify:

- **Dead code**: variables, functions, classes, imports with zero inbound edges; unreachable blocks after `return`/`break`. Follow cascades: if removing `FuncA` leaves `FuncB` with zero references, flag `FuncB` too.
- **Stale code**: commented-out blocks, outdated markers. Recommend removal; Git history preserves them.
- **Docstring violations**: Google-style sections (`Parameters:` / `Args:` / `Returns:` with a colon, or `name (type): text`), missing `Parameters`/`Returns`, summaries that state the result instead of the mechanism, PEP 257 breaches. Google-style docstrings do not render under numpydoc and must be converted.

## Phase 3 — Gate (stop and report)

Modify nothing yet. Report in this exact structure, then wait for explicit approval:

1. **Graph sync status** — confirmation of the Phase 1 sync.
2. **Dead and stale code** — bulleted deletion candidates, with cascade warnings.
3. **Docstring diff** — before/after blocks. Flag separately any rewrite that is a Google-to-numpydoc conversion rather than new content; those change rendering, not meaning.
4. **Approval prompt** — a direct question asking permission to execute.

## Phase 4 — Execute and verify

Once approved, apply the changes. Then:

- Run the docstring checker: `python scripts/validate_docstrings.py`, or `python -m numpydoc.hooks.validate_docstrings <module>` if the project has none. `PR01`, `RT01`, `SS05` or `SS06` on a function just rewritten means the section syntax is still wrong. Exclusions and false positives are listed in `docstrings.md`.
- Run the test suite (`pytest -q`).
- Investigate every failure. If a change broke something, revert that specific change and report it. The codebase stays 100% functional.

## Phase 5 — Final sync

Only when the codebase is clean, functional and error-free: run `/graphify <project root> --update --mode deep` once more.
