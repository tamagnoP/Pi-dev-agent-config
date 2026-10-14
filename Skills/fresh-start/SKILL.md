---
name: fresh-start
description: Bootstrap a brand-new Python package so it is clean, provable and publishable from the first commit — git and .gitignore, src-layout pyproject, environment, pytest, ruff with an explicit rule set, enforced numpydoc docstrings, a Sphinx docs/ built with -W, GitHub Actions CI, .readthedocs.yaml, CHANGELOG, and the TODO/DECISIONS/option-testing tracking files. Use this skill when the user starts a new project, repository, package or CLI tool from scratch, says "new project", "from the ground up", "set up a repo", "scaffold", or asks how to make a package clean, citable or publishable before the code exists.
---

# Fresh Start — the bootstrap workflow for a new Python package

This is the required order for standing up a new package. Work through the
phases in sequence. Each phase ends with a **gate**: a command that passes or
fails. Do not advance past a failing gate, and do not reorder phases.

## Core rule

**Every standard is installed together with the command that enforces it.**

A standard with no failing command is a preference. In the same commit that
introduces a rule, add the check that fails when the rule is broken.

## Invariants

These hold for every project built with this skill.

1. **Documentation infrastructure exists before the second module.** A
   documentation build can only cover a release whose own checkout contains
   `docs/conf.py`. Any release tagged before `docs/` exists is permanently
   undocumentable.
2. **A convention is written to its checker, never audited into it later.**
3. **A linter runs with an explicit rule set, and its clean state is zero.** A
   tolerated non-zero baseline does not go down.
4. **Any environment that runs an import-based check must be able to import the
   whole package.** A module that cannot be imported is skipped silently and
   passes by being invisible.
5. **Data never enters the repository.** The repository holds code and the
   record of how it was run.

## Required inputs

Ask the user for these before writing any file. Do not assume an answer; each
one determines the content of a file below.

1. **Package name**, and whether it is free on PyPI (`pip index versions <name>`).
2. **License.** If the user is undecided, state the difference: permissive
   (MIT/BSD/Apache-2.0) allows closed-source reuse; copyleft (GPL/AGPL)
   requires derivatives to stay open.
3. **Minimum Python version.**
4. **Public now, or public later.** This determines only the Read the Docs
   phase; the free tier builds public repositories only.
5. **Optional or heavy dependencies** (GPU, GUI, 3D, domain stacks). These
   become extras and determine what CI and the documentation build install.

---

## Phase 1 — Git, and `.gitignore` as the first commit

```bash
git init -b main
```

Write `.gitignore` from `templates/gitignore.txt` before any other file exists,
then commit it alone:

```bash
git add .gitignore && git commit -m "Ignore rules, before anything can be committed by accident"
```

Rules that apply from here on:

- One commit per coherent unit, never per file. A partially copied package does
  not import, so a per-file commit is a broken state.
- Run the phase gates before committing.
- The commit message states why; the diff states what.
- No data, credentials, environments or build outputs are ever committed.

**Gate:** `git log --oneline` shows one commit; `git status` is clean.

---

## Phase 2 — `pyproject.toml` and the package skeleton

Copy `templates/pyproject.toml` and substitute the required inputs. Create
`src/<package>/__init__.py`, `tests/`, `scripts/`.

Required choices:

- **`src/` layout.** Without it, an import in the test suite can resolve to the
  working directory instead of the installed package, and tests pass against
  code that was never packaged.
- **Declare a `[project.scripts]` entry only in the commit that adds its
  `main()`.** A command declared earlier installs and then fails on first use.
- **Core dependencies are only what the main chain imports.** Everything else
  is an extra. Extras determine what CI, the documentation build and a first
  user install actually pull.
- **`version = "0.0.1"`**, climbing only as described in Phase 11.

**Gate:**

```bash
pip install -e .
python -c "import <package>; print(<package>.__version__)"
```

Note: `tomllib` is standard library from 3.11; on 3.10 use `tomli`. The install
is the real gate, since it parses the file, resolves the extras and builds the
wheel. It also catches an `all = ["<package>[extra]"]` entry pointing at an
extra that is not declared, which fails with
`ValueError: Unknown recursive dependency group`.

---

## Phase 3 — The declared environment

Create one named environment and record its contents.

```bash
conda create -n <project>_venv python=3.X -y     # or python -m venv .venv
pip install -e ".[dev]"
```

Write `environment.yml` or a pinned `requirements-dev.txt`.

**Any dependency that a gate needs is a requirement of the development
environment, not an optional extra.** If a check skips when a package is
absent, an environment without that package runs green while enforcing nothing.
Declare such packages in both `pyproject.toml` and the environment file, and
add a test asserting the two agree.

**Gate:** `pip check` is clean, and the test comparing declared dependencies
with the environment file passes.

---

## Phase 4 — Tests, starting with the first module

`tests/` exists before the first module is finished.

- Mirror the package layout: `tests/core/test_config.py` for
  `src/<package>/core/config.py`.
- `conftest.py` holds fixtures only.
- A test name states what must be true, for example
  `test_it_refuses_an_unknown_config_key`.
- **Write a test for every refusal:** an unknown config key refused by name, a
  missing file reported with its path, an out-of-range index explained. A
  silently ignored setting is indistinguishable from one that did not work.
- Guard optional dependencies with `pytest.importorskip` at the top of the
  module, so a core-only install skips instead of erroring during collection.
  A collection error interrupts the entire run.

**Gate:** `pytest -q` passes. Record the count in the commit message.

---

## Phase 5 — `ruff` with an explicit rule set

Never run the linter on defaults. Select the rules the project enforces and
comment what each family catches.

```toml
[tool.ruff.lint]
select = ["E4", "E7", "E9", "F", "W292", "RUF100", "I001", "ARG"]
```

- `E4/E7/E9` import placement, statement and syntax errors
- `F` undefined names, unused imports and variables
- `W292` missing newline at end of file
- `RUF100` a `noqa` that no longer suppresses anything
- `I001` unsorted imports
- `ARG` an argument accepted and never used

Per-file ignores require a written reason. Tests normally need `ARG` (a test
double takes the signature of what it replaces) and `E402` (`importorskip` must
precede the imports it guards).

**Gate:** `ruff check src tests` reports zero.

---

## Phase 6 — Docstrings enforced by a checker

Use numpydoc (NumPy style) from the first docstring.

Copy `templates/validate_docstrings.py` to `scripts/` and
`templates/test_docstring_schema.py` to `tests/`. The script walks the public
API and calls `numpydoc.validate`; the test fails the suite on any violation.

Two exclusions, applied in the template and recorded in writing:

- **Checks that cannot pass** on a codebase that does not write those sections:
  `SA01` (See Also) and `EX01` (Examples) fire on every object, and `ES01`
  (extended summary) fires on complete one-line docstrings.
- **Objects the checker cannot read:** `Enum` subclasses and `typing.Protocol`
  classes report metaclass parameters as undocumented. Exclude the objects, not
  the checks.

Content requirements:

- State how the code works and why it is built that way. The signature already
  states what is returned.
- Document every refusal: what triggers it and what the caller should do.
- A constant that encodes a decision carries that decision above it.

**Gate:** `python scripts/validate_docstrings.py` exits 0, and `pytest` fails
when it would not.

---

## Phase 7 — `docs/`, built with `-W`

Set this up when the package has one module. See Invariant 1.

Copy `templates/docs_conf.py`, `templates/docs_index.md`,
`templates/docs_api_index.rst` and `templates/docs_Makefile` into `docs/`.

Required configuration:

- **Recursive `autosummary`** over the top-level package, so a new module is
  documented without being listed by hand.
- **Do not re-run the docstring schema validation inside the build.** The test
  suite already enforces it, and numpydoc's Sphinx hook has no equivalent of
  the `Enum`/`Protocol` exclusion, so the two gates would disagree on what
  counts as clean. The build enforces the separate claim that the docstrings
  render.
- **The documentation environment installs every extra** (Invariant 4).
- **`-a -E` in the strict target.** Autosummary stubs are cached, and a cached
  stub hides a fault that a cold build reports.

This build catches faults no docstring checker can see: an indented block read
as a block quote, a definition or enumerated list ending without a blank line,
`|x|` read as an undefined substitution reference, a short title underline. The
usual fix is to end the introducing sentence with `::` so the block renders
literally.

**Gate:** `cd docs && make strict` reports `build succeeded` with zero
warnings.

---

## Phase 8 — Continuous integration

Copy `templates/workflow_ci.yml` and `templates/workflow_docs.yml` into
`.github/workflows/`.

- **`ci.yml`** installs `.[dev]`, then runs `ruff check src tests`, `pytest`,
  and the docstring validator as a standalone step so a skipped test cannot
  pass as a green run.
- **`docs.yml`** installs `.[all,docs]` plus any system libraries the heavy
  extras need, asserts that every module imports, then runs
  `sphinx-build -W --keep-going -a -E`.

The explicit import step converts a silent autosummary skip into a failure.

**Gate:** both workflows pass, and branch protection requires both.

---

## Phase 9 — `.readthedocs.yaml`

Copy `templates/readthedocs.yaml` to the repository root. Commit it even if the
repository is private: it is inert until the project is connected on
readthedocs.org, and committing it keeps the recipe from drifting from the
`docs/` it describes.

State these two constraints to the user:

- The free tier builds public repositories only; a private repository requires
  the paid tier.
- The version list starts at the first tag cut after `docs/` is committed
  (Invariant 1).

Before relying on the free tier, measure the build against its limits
(15 minutes, 3 GB): time a cold `pip install --no-cache-dir` and a cold
`sphinx-build` with `/usr/bin/time -l` (macOS) or `-v` (Linux), and record the
numbers in `DECISIONS.md`. If the measurement exceeds the limits, reduce the
extras or mock the heaviest imports, and record which modules that leaves
unverified.

**Gate:** the YAML parses, uses only valid v2 top-level keys, and `pytest` and
`ruff` results are unchanged by its presence.

---

## Phase 10 — `CHANGELOG.md`

Copy `templates/CHANGELOG.md`. Keep a Changelog format, Semantic Versioning.
Write each entry in the same commit as the change it describes.

An entry carries:

- **the measurement**, where one exists, not an adjective;
- **what it breaks** — if results produced before a change are not comparable
  with results produced after it, state that explicitly and name the file that
  records which version produced a given result;
- **what was rejected**, where the alternative was measured.

**Gate:** a test asserts `CHANGELOG.md` contains an entry for the version
declared in `pyproject.toml`.

---

## Phase 11 — The version ladder

| version | meaning |
|---|---|
| 0.0.1 | name reserved, no functionality |
| 0.x.0 | one coherent subsystem works, with tests and a real-input check |
| 1.0.0 | the whole package runs end to end, documented |

Each release requires: tests passing, `ruff` zero, documentation build clean,
`CHANGELOG.md` updated, then `git tag vX.Y.Z`.

---

## Phase 12 — Tracking files

Create these in the bootstrap commit.

**`TODO.md`** (template provided) — the single source of truth for task state,
updated as each task completes. A completed task records its evidence: test
count, timing, the measurement that settled it, the path to its log.

**`DECISIONS.md`** — one entry per non-obvious choice: the question, the
options tested, the empirical result of each, the choice and the reason.
Refuted proposals are recorded with their evidence so they are not reopened
from the same reasoning.

**`option-testing/<DECISION-ID>_isolated_tests/`** — the raw logs behind each
decision, one directory per decision, never importable from `src/`.

When a choice is ambiguous, build the alternatives, measure them, write the
logs, then present the options with their numbers for the user to choose.

If the user maintains their own `DECISIONS_TEMPLATE.md` and `TEST_TEMPLATE.md`,
use those formats.

---

## Phase 13 — Provenance in the outputs

From the first module that writes anything:

- Write `run.log` and `config.used.yaml` beside every output, so a result can be
  traced to the settings that produced it.
- Record the decisive method choices in a machine-readable file beside the
  results, so two runs can be distinguished afterwards.
- Refusals name the file, key, index or accepted values.

---

## Phase 14 — Release dry run

```bash
python -m build
twine check dist/*
python -m venv /tmp/fresh && /tmp/fresh/bin/pip install dist/*.whl
/tmp/fresh/bin/<console-script> --help
```

Testing the built artifact rather than the working tree catches a package
missing from the wheel target, a data file that never shipped, and a console
script pointing at an unpackaged module.

**Gate:** the console script runs in a clean environment that has never seen
the source tree.

---

## Templates

In `templates/`, next to this file. Substitute `PACKAGE_NAME`, `AUTHOR`,
`EMAIL`, `USER` and `YEAR`.

| template | destination |
|---|---|
| `gitignore.txt` | `.gitignore` |
| `pyproject.toml` | `pyproject.toml` |
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
| `TODO.md` | `TODO.md` |

---

## Bootstrap checklist

```text
[ ] 1  git init; .gitignore is commit #1
[ ] 2  pip install -e . succeeds; no console script declared before its module
[ ] 3  named environment; pip check clean; gate tools declared in the env file
[ ] 4  pytest -q passes, including a test for a refusal
[ ] 5  ruff check src tests -> 0
[ ] 6  python scripts/validate_docstrings.py -> 0, enforced by the suite
[ ] 7  cd docs && make strict -> build succeeded, 0 warnings
[ ] 8  ci.yml and docs.yml pass and are required by branch protection
[ ] 9  .readthedocs.yaml parses, is inert, and the build fits the limits
[ ] 10 CHANGELOG.md has an entry for the declared version
[ ] 11 version is 0.0.1 and climbs only per Phase 11
[ ] 12 TODO.md, DECISIONS.md, option-testing/ exist
[ ] 13 run.log and config.used.yaml written beside outputs
[ ] 14 the built wheel runs in a clean environment
```

## Out of scope

Add these only when the user asks for them; they are not part of this workflow:
coverage thresholds, pre-commit hooks, release automation, and a hand-written
narrative documentation site (the generated API reference plus `README.md`
cover the same ground, and the README's paths and commands can be tested).
