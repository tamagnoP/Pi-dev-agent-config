---
name: fresh-start
description: Bootstrap the repository infrastructure of a brand-new Python package, from the first commit to a release dry run, with every standard installed next to the command that enforces it. Use when the user starts a new project, repository, package or CLI tool from scratch, says "new project", "from the ground up", "set up a repo", "scaffold", or asks how to make a package clean, citable or publishable before the code exists. Runs once per project; for the code inside src/, use writing-python.
---

# Fresh Start

Stand up a new package in the phases below, in order. Each phase ends with a
**gate**: a command that passes or fails. Do not advance past a failing gate.

Templates live in `/Users/Office/.pi/agent/skills/fresh-start/templates/`. Each
carries its own rationale as comments, so the *why* ships with the project;
this page says only what to copy, what to decide, and what gate to run.
Read a template at the moment its phase copies it, not before.

## Core rule

**Every standard is installed together with the command that enforces it.** A
standard with no failing command is a preference. The rule and its checker
land in the same commit.

## Invariants

1. **`docs/` exists before the second module.** A documentation build covers
   only a release whose own checkout contains `docs/conf.py`; a tag cut before
   that is permanently undocumentable.
2. **A convention is written to its checker, never audited into it later.**
3. **The linter runs an explicit rule set, and its clean state is zero.**
4. **Any environment that runs an import-based check must import the whole
   package.** A module that cannot be imported is skipped and passes by being
   invisible.
5. **Data never enters the repository.** The repository holds code and the
   record of how it was run.

## Required inputs

Ask before writing any file; each answer determines a template substitution.

1. **Package name**, and whether it is free on PyPI (`pip index versions <name>`).
2. **License.** If undecided: permissive (MIT/BSD/Apache-2.0) allows
   closed-source reuse; copyleft (GPL/AGPL) requires derivatives to stay open.
3. **Minimum and maximum Python version** to support.
4. **Public now, or later.** Affects only Phase 9: the free Read the Docs tier
   builds public repositories only.
5. **Optional or heavy dependencies** (GPU, GUI, 3D, domain stacks). They
   become extras and decide what CI and the docs build install.

## Substitutions

| placeholder | value |
|---|---|
| `PACKAGE_NAME` | the package name |
| `ONE_LINE` | one line, what it does — not what it aspires to |
| `LICENSE_ID` | SPDX identifier, e.g. `MIT` |
| `AUTHOR`, `EMAIL`, `USER`, `YEAR` | author name, e-mail, GitHub user, current year |
| `PY_MIN`, `PY_MAX` | e.g. `3.10`, `3.13` |

Substitute in every template as it is copied.

---

## Phase 1 — Git, `.gitignore` as the first commit

```bash
git init -b main
```

Copy `gitignore.txt` → `.gitignore`. Commit it alone.

From here on: one commit per coherent unit, never per file; run the phase
gates before committing; the message says why, the diff says what; tell the
user before any Git command that changes state.

**Gate:** `git log --oneline` shows one commit; `git status` is clean.

## Phase 2 — `pyproject.toml` and the skeleton

Copy `pyproject.toml`. Create `src/<package>/__init__.py`, `tests/`,
`scripts/`, `README.md`, `LICENSE`.

Decide: core dependencies (only what the main chain imports) and extras
(everything else, grouped by the stage that needs them). Leave
`[project.scripts]` empty until a `main()` exists.

**Gate:**

```bash
pip install -e . && python -c "import <package>"
```

## Phase 3 — The declared environment

Copy `environment.yml` and `test_environment.py` → `tests/`.

```bash
conda env create -f environment.yml && conda activate <package>_venv
```

**Gate:** `pip check` clean; `pytest tests/test_environment.py -q` passes.

## Phase 4 — Tests, before the first module is finished

- `tests/` mirrors `src/<package>/` one-to-one: `tests/test_<module>.py`.
- `conftest.py` holds fixtures only.
- A test name states what must be true: `test_it_refuses_an_unknown_config_key`.
- **Every refusal has a test**: unknown key refused by name, missing file
  reported with its path, out-of-range value explained.
- Guard optional dependencies with `pytest.importorskip` at the top of the
  module, so a core-only install skips instead of breaking collection.

**Gate:** `pytest -q` passes. Record the count in the commit message.

## Phase 5 — Ruff

The rule set and per-file ignores are in `pyproject.toml` with their reasons.
Any new ignore carries a written reason.

**Gate:** `ruff check src tests` and `ruff format --check src tests` → 0.

## Phase 6 — Docstrings enforced by a checker

numpydoc from the first docstring. The schema and the writing rules are in
`/Users/Office/.pi/agent/skills/writing-python/references/docstrings.md`.

Copy `validate_docstrings.py` → `scripts/` and `test_docstring_schema.py` →
`tests/`. The exclusions and their reasons are in the script's docstring.

**Gate:** `python scripts/validate_docstrings.py` → 0, and `pytest` fails when
it would not.

## Phase 7 — `docs/`, built with `-W`

Set up when the package has one module (Invariant 1).

Copy `docs_conf.py` → `docs/conf.py`, `docs_index.md` → `docs/index.md`,
`docs_api_index.rst` → `docs/api/index.rst`, `docs_Makefile` → `docs/Makefile`.
`pip install -e ".[all,docs]"`.

This build catches what the schema checker cannot: an indented block read as a
block quote, a list ending without a blank line, `|x|` read as a substitution,
a short title underline. The usual fix is ending the introducing sentence with
`::` so the block renders literally.

**Gate:** `cd docs && make strict` → `build succeeded`, zero warnings.

## Phase 8 — Continuous integration

Copy `workflow_ci.yml` → `.github/workflows/ci.yml` and `workflow_docs.yml` →
`.github/workflows/docs.yml`. If no extra needs OpenGL, delete the system
libraries step from `docs.yml` and the `apt_packages` block from
`readthedocs.yaml` (Phase 9).

**Gate:** both workflows pass; branch protection requires both.

## Phase 9 — `.readthedocs.yaml`

Copy `readthedocs.yaml` → `.readthedocs.yaml`, public or not. State the two
constraints in its header to the user.

Measure the build against the free-tier limits (15 min, 3 GB): time a cold
`pip install --no-cache-dir` and a cold `sphinx-build` with
`/usr/bin/time -l` (macOS) or `-v` (Linux); record the numbers in
`DECISIONS.md`. If over, reduce the extras or mock the heaviest imports, and
record which modules that leaves unverified.

**Gate:** the YAML parses with only valid v2 keys; `pytest` and `ruff` are
unchanged by its presence.

## Phase 10 — `CHANGELOG.md` and the version ladder

Copy `CHANGELOG.md` and `test_changelog_version.py` → `tests/`. Entries are
written in the same commit as the change; what an entry carries is in the
file's header. The version ladder and release requirements are in `TODO.md`.

**Gate:** `pytest tests/test_changelog_version.py -q` passes.

## Phase 11 — Tracking files

Copy `TODO.md`; its Bootstrap section is this skill's checklist, so tick items
there as the gates pass. Create `DECISIONS.md` from
`/Users/Office/.pi/agent/templates/DECISIONS_TEMPLATE.md` and an empty
`option-testing/`. Ambiguous choices follow
`/Users/Office/.pi/agent/templates/AMBIGUITY_PROTOCOL.md`.

Provenance in outputs (`run.log`, `config.used.yaml`) belongs to each module
and is specified in `writing-python`.

**Gate:** all three exist; `TODO.md` reflects the gates passed so far.

## Phase 12 — Release dry run

```bash
python -m build && twine check dist/*
python -m venv /tmp/fresh && /tmp/fresh/bin/pip install dist/*.whl
/tmp/fresh/bin/python -c "import <package>"
/tmp/fresh/bin/<console-script> --help      # only once one is declared
```

Testing the built wheel catches a package missing from the wheel target, a
data file that never shipped, and a script pointing at an unpackaged module.

**Gate:** the wheel installs and imports in an environment that has never seen
the source tree.

---

## Templates

| template | destination |
|---|---|
| `gitignore.txt` | `.gitignore` |
| `pyproject.toml` | `pyproject.toml` |
| `environment.yml` | `environment.yml` |
| `test_environment.py` | `tests/test_environment.py` |
| `validate_docstrings.py` | `scripts/validate_docstrings.py` |
| `test_docstring_schema.py` | `tests/test_docstring_schema.py` |
| `docs_conf.py` | `docs/conf.py` |
| `docs_index.md` | `docs/index.md` |
| `docs_api_index.rst` | `docs/api/index.rst` |
| `docs_Makefile` | `docs/Makefile` |
| `workflow_ci.yml` | `.github/workflows/ci.yml` |
| `workflow_docs.yml` | `.github/workflows/docs.yml` |
| `readthedocs.yaml` | `.readthedocs.yaml` |
| `CHANGELOG.md` | `CHANGELOG.md` |
| `test_changelog_version.py` | `tests/test_changelog_version.py` |
| `TODO.md` | `TODO.md` |

## Out of scope

Add only when the user asks: coverage thresholds, pre-commit hooks, release
automation, a hand-written narrative docs site (the generated API reference
plus `README.md` cover it, and the README's commands can be tested).
