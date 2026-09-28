---
name: writing-python
description: Coding standards and codebase architecture for Python scientific analysis pipelines, standalone scripts and CLI utilities. Use this skill whenever the user asks to write, refactor, review, clean up, extend or delete any Python code, module, script, CLI tool, data-processing step or analysis pipeline — even if they don't mention "standards", "architecture" or "best practices". Also use it when adding or removing features, methods or modules in an existing Python project, or when editing pipeline configuration.
---

# Python Pipeline Standards

Apply these standards whenever you write, refactor, extend or delete Python code in this project.

## Workflow

- **Writing from scratch:** follow every rule below and the architecture in section 8.
- **Refactoring:** before changing anything, ask the user whether to scan the full codebase or a specific directory. Follow their answer exactly. Then follow the refactoring procedure in section 9.
- **Adding or deleting a module or feature:** follow the procedures in section 9. Do not skip the impact check.
- **Version control:** tell the user before running any Git command that changes state (`add`, `commit`, `push`, branch creation, etc.).
- **Before reporting "done":** run the checklist in section 11.

## Non-negotiable rules

These five rules override any convenience shortcut. Check them first when reviewing or writing code.

1. **Every module owns its own YAML config.** One module, one config file, one purpose. No global config file, no shared mega-YAML, no parameters in code, environment variables, `.env` files or CLI flags. Each module's CLI takes `--config path/to/<module>.yaml` and nothing else that changes behavior.
2. **Every module runs standalone.** `python -m <package>.<module> --config config/<module>.yaml` must work on its own, without any orchestrator. A module never imports another module.
3. **The code is data-agnostic.** Never hardcode column names, variable names, units, sample IDs, group labels, sheet names or file schemas. Read them from the input files (headers, metadata, index) at load time. When a module needs a specific variable, the user names it in that module's YAML and the module validates that it exists in the data before running.
4. **No abstraction layers.** No registries, no plugin systems, no `enabled` flags, no base classes, no inheritance, no factories, no dependency injection, no wrapper indirection, no result-metadata objects. A module reads its config, loads its data, does its work with direct function calls, and writes its outputs. The flow must be readable top to bottom.
5. **Every line earns its place.** If a task reads clearly in 5 lines, it must not take 10. Delete clutter, redundancy and ceremony — never functionality. Shorter only wins when it is still obvious to read, follow and maintain.

## 1. Execution structure

- Every module is a script with one job. Put all execution logic in `main()`. Never leave executable code in the global scope.
- `main()` returns an exit code; `sys.exit` is called only in the guard block. This keeps `main()` testable, importable by the runner, and keeps `sys.exit` out of business logic:
  ```python
  def main(config_path: Path | None = None) -> int:
      path = config_path or parse_args().config
      config = load_config(path)
      configure_logging(config.log_level, config.output_dir)
      try:
          run(config)
      except PipelineError as exc:
          logger.error("%s failed: %s", MODULE_NAME, exc)
          return 1
      return 0

  if __name__ == "__main__":
      sys.exit(main())
  ```
- `main()` accepts an optional config path so `scripts/run_all.py` can call it directly instead of shelling out.
- Return `0` on success and a non-zero code on any fatal error. Shell pipelines, cron jobs and CI runners depend on these codes.

## 2. Command-line arguments

- Parse arguments with `argparse` in a dedicated `parse_args()` function. Never index `sys.argv` directly.
- Give every argument a type (`type=Path`, `type=int`, ...), a `help` string, and mark it `required=True` when it is.
- The CLI accepts `--config` (required, `type=Path`) and optionally `--dry-run` / `--verbose`. Every scientific parameter comes from the module's YAML, never from a flag.
- The CLI only collects the config path and calls `main()`. No processing logic lives in argument parsing.

## 3. Paths and files

- Use `pathlib.Path` for all filesystem paths. No string concatenation, no `os.path`.
- Never hardcode absolute paths. Anchor project-relative paths to the script's own location:
  ```python
  BASE_DIR = Path(__file__).resolve().parent
  ```
- Input and output locations come from the module's YAML config, never from literals inside processing code.

## 4. Logging

- Use the `logging` module for all status output. No `print()` for progress, diagnostics or errors.
- Configure logging exactly once per run, in `main()`, via `logging.basicConfig(...)`. Every module gets its own logger at the top of the file:
  ```python
  logger = logging.getLogger(__name__)
  ```
  Never call `logging.info(...)` on the root logger from inside processing code.
- Match the level to the meaning:
  | Level | Use for |
  |---|---|
  | `debug` | execution traces, intermediate values |
  | `info` | module start and end, normal progress |
  | `warning` | non-fatal problems, retries, fallbacks |
  | `error` | failures |
- At the start of a run, log the module name, the input path and the resolved configuration. Write the same log to `<output_dir>/run.log`.

## 5. Types and error handling

- Follow PEP 8.
- Annotate every function: all parameters and the return type. Use `int | None`, not `Optional[int]`.
- Represent config and loaded data with `@dataclass(frozen=True)`, never with loose dicts or tuples passed between functions. Frozen dataclasses make invalid or half-built states hard to create. Keep them flat — fields and nothing else. No methods beyond a `load`/`from_yaml` classmethod where it genuinely shortens the code.
- Wrap external interactions (file I/O, network, subprocess, system calls) in `try/except`. Scripts run unattended, so on failure: log a concrete error message, then exit non-zero.
- Never write a bare `except:` or `except Exception:` that only logs and continues. Catch specific exceptions; if you must catch broadly, re-raise or convert to a fatal exit. Silent failures are worse than crashes.
- Define a small project exception hierarchy in `errors.py`:
  ```python
  class PipelineError(Exception): ...
  class ConfigError(PipelineError): ...   # bad or missing YAML values
  class DataError(PipelineError): ...     # variable not in input, wrong shape, bad values
  ```

## 6. Code style

- **Names reveal intent.** Descriptive names for variables, functions and classes. No abbreviations, no single-letter names. A reader should not have to decode a name.
- **Small functions, flat logic.** Use guard clauses and early returns instead of nested `if` blocks. Keep every function at a single level of abstraction: high-level flow in one place, low-level detail in another.
- **Write it once, write it short.** Prefer the shortest version that stays obvious: comprehensions over accumulator loops, direct returns over temporary variables that are used once, standard-library and pandas/numpy built-ins over hand-rolled loops. Stop shortening the moment the code stops being obvious.
- **Cut the ceremony.** No getters/setters, no one-line wrapper functions that only call another function, no defensive re-validation of values already validated in `load_config`, no dead parameters, no unused "for later" hooks (YAGNI).
- **Keep changes focused.** One refactor or feature per change; don't mix unrelated edits.
- **Docstrings and comments explain *why*.** Add a docstring when a function or module needs explanation of its behavior or contract. Comments explain decisions, not restate the code.
- **Don't pessimize.** Avoid obviously wasteful patterns (loading whole files when streaming works, quadratic loops over large data) but never add complexity for speculative performance gains.
- **Formatting is automated.** Ruff handles both linting and formatting, configured in `pyproject.toml`. Before finishing any task, run:
  ```bash
  ruff check --fix . && ruff format .
  ```

## 7. Design principles

- **Simplicity first (KISS).** Choose the most straightforward design that works. Add complexity only when a real constraint demands it.
- **Directness over indirection.** Call the function. Do not route the call through a registry, a dispatcher, a config key or a class hierarchy. If a reader has to jump through two files to find what runs, the design is wrong.
- **Single source of truth (DRY).** Each piece of knowledge lives in exactly one place. For a module's parameters, that place is its YAML.
- **One module, one job.** Each module has one reason to change. If a module needs an "and" to describe it, split it.
- **Modules are independent.** Modules never import each other. They communicate only through files on disk: one module's output path is the next module's input path, set by the user in each YAML.
- **Shared code is small and dumb.** Only genuinely generic helpers (YAML loading, logging setup, output directory creation) live in `common.py`. `common.py` holds no domain knowledge and no branching on module names.
- **Separate decisions from side effects.** Compute *what* to do in pure functions; perform I/O at the edges of the module.
- **Design for failure.** Expect missing files, missing variables, bad input and resource limits; don't build only the happy path. Every failure produces a message a human can understand and act on.

## 8. Codebase architecture

### 8.1 Layout

Use this structure. Create missing directories when adding the first file that belongs there; do not invent alternative layouts.

```
project/
├── pyproject.toml           # REQUIRED: dependencies, ruff, pytest config. No setup.py, requirements.txt or ruff.toml.
├── README.md                # what each module does, in run order, with its config file
├── config/
│   ├── extract_features.yaml    # one YAML per module, same name as the module
│   ├── filter_cells.yaml
│   └── classify_cells.yaml
├── notebooks/               # exploration only; imports from src/
├── scripts/
│   └── run_all.py           # thin runner: calls each module's main() in a literal fixed order
├── src/<package>/
│   ├── __init__.py
│   ├── errors.py            # PipelineError, ConfigError, DataError
│   ├── common.py            # load_yaml, configure_logging, prepare_output_dir — generic only
│   ├── extract_features.py  # standalone module: Config, load_config, run, main
│   ├── filter_cells.py
│   └── classify_cells.py
└── tests/                   # mirrors src/<package>/ one-to-one
```

- Modules live flat in `src/<package>/`. No `processing/`, `analysis/`, `visualization/` sub-packages — the file name says what the module does.
- Input data and outputs live wherever the user's YAML points; they are never inside the repository unless the user chooses that.

### 8.2 Module anatomy

Every module file has the same five parts, in this order. A reader opening any module knows exactly where to look.

1. `logger` and `MODULE_NAME`.
2. `@dataclass(frozen=True) class Config` — every parameter the module accepts.
3. `def load_config(path: Path) -> Config` — read YAML, validate, raise `ConfigError` naming the bad key.
4. The work: a handful of small, pure functions, then `def run(config: Config) -> None` that loads the input, calls them in order and writes the outputs.
5. `parse_args()`, `main()`, `if __name__ == "__main__": sys.exit(main())`.

Rules:

- `run()` is the readable summary of the module: load → validate variables → process → write. Keep it short enough to read in one screen.
- A module never imports another module in the package. It may import `errors.py` and `common.py`.
- All tunable values come from `Config`. No magic numbers in the work functions.
- Validate every user-named variable against the loaded data immediately after loading, before any processing. Raise one `DataError` listing every missing variable — not one failure per variable.
- Work functions are pure: they take data and plain values, return data, and do not touch the filesystem. Reading and writing happen in `run()`.
- Deterministic: same input, same config, same seed → same output. Seeds come from the YAML, never from time.
- Failures raise a `PipelineError` subclass with a message naming the module, the input and what was wrong.

### 8.3 The runner

`scripts/run_all.py` is the only place that knows the full order. It stays trivial:

```python
from pathlib import Path
import sys

from mypackage import classify_cells, extract_features, filter_cells

CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"

STEPS = [
    (extract_features.main, "extract_features.yaml"),
    (filter_cells.main, "filter_cells.yaml"),
    (classify_cells.main, "classify_cells.yaml"),
]


def main() -> int:
    for step, config_name in STEPS:
        code = step(CONFIG_DIR / config_name)
        if code != 0:
            return code
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- The runner contains no processing logic, no config parsing and no conditionals beyond the failure check. It stops at the first non-zero exit code.
- Adding a module means adding one line to `STEPS`. Nothing else in the runner changes.
- The runner is optional convenience. Every module must still work when run alone.

### 8.4 Data-agnostic loading

- Load functions return a frozen dataclass holding the data plus whatever metadata was discovered: variable names, units if present, sample identifiers, source path.
- Loaders infer schema from the file (headers, index, attributes). They never take a hardcoded list of expected columns.
- `load_config` cannot check variable names (the data isn't loaded yet), so `run()` validates them against the loaded data before processing.

### 8.5 Output directory

Each module's YAML sets its own `output_dir`. The module writes, flat, into that directory:

```
<output_dir>/
├── run.log                  # this module's log for this run
├── config.used.yaml         # the exact config used, defaults filled in
├── <result>.csv             # the module's results
└── <figure>.png
```

Rules:

- **One level, no nesting.** The user opens the directory and sees the results, the log and the config that produced them. Nothing else.
- **Plain names.** `filtered_cells.csv`, not `fc_v2_final.csv`.
- A module writes only inside its own `output_dir`. Never write into the input data directory, and never into another module's `output_dir`.
- `common.py` owns directory creation and the `config.used.yaml` dump in one function each. No module builds these by hand.
- Chaining is explicit: the user sets the next module's `input_path` to a file in the previous module's `output_dir`.

### 8.6 Configuration schema

One YAML per module, named after the module, living in `config/`. `load_config` reads it into the module's frozen `Config`, rejecting unknown keys, missing required keys and out-of-range values with a `ConfigError` that names the key.

```yaml
# config/filter_cells.yaml
input_path: /data/experiment_01/features.csv
output_dir: /results/experiment_01/filter_cells

log_level: INFO
seed: 42

variables: [area, intensity_mean]   # must exist in the input file
method: iqr                         # iqr | zscore
factor: 1.5
```

Rules:

- **Flat by default.** Nest only when a group of parameters genuinely belongs together. No `stages:` tree, no per-method sub-blocks, no `enabled` flags — a module runs because the user ran it.
- Every config file contains only the keys its own module uses. A key that no module reads is a bug.
- Each config file is committed with working defaults and a one-line comment per parameter. It is the documentation of what the module can do.
- Keys map one-to-one onto `Config` fields. A test checks that every YAML in `config/` loads into its module's `Config` without error.

### 8.7 Notebooks

- Notebooks are for exploration and reporting only. They import functions from `src/<package>/`; they never contain logic that a module depends on.
- If logic in a notebook becomes reusable, move it into a module and add a test.

## 9. Change procedures

### 9.1 Adding a module

1. Confirm no existing module already does this (DRY). Search `src/` before writing.
2. Create `src/<package>/<module>.py` following the anatomy in 8.2.
3. Create `config/<module>.yaml` with every parameter, working defaults and one-line comments.
4. Add one line to `STEPS` in `scripts/run_all.py`, in the correct position.
5. Add `tests/test_<module>.py` covering normal input, a missing-variable failure and a bad-config failure.
6. Add the module to `README.md` in run order, stating its input and output.
7. Do not touch other modules. If you had to, module independence is being violated — stop and ask.

### 9.2 Adding a feature to an existing module

1. Confirm it belongs to that module's one job. If it needs an "and" to describe, it is a new module — ask the user.
2. Add its parameters to `Config`, `load_config` validation and `config/<module>.yaml`.
3. Keep `run()` readable; if it no longer fits on a screen, extract a named work function — not a new layer.
4. Add tests for the new behavior.

### 9.3 Deleting a module or feature

1. Find every reference: `grep -rn "<name>" src/ tests/ scripts/ notebooks/ config/`.
2. List the affected files to the user before deleting anything.
3. Check whether any other module's YAML points at its `output_dir` as an input. If so, stop and ask the user: that chain breaks.
4. Remove the code, its tests, its `config/<module>.yaml`, its line in `STEPS` and its `README.md` entry.
5. Make `load_config` reject removed keys so stale user YAMLs fail loudly rather than silently ignoring them.
6. Remove now-unused imports and helpers (`ruff check` will flag them).
7. Run the full test suite. Deletion is complete only when it passes.

### 9.4 Refactoring

1. Ask the user for scope (full codebase or a directory). Stay inside it.
2. Run the test suite first. If tests are missing for the code being refactored, write characterization tests that capture current behavior before changing anything.
3. Make one kind of change at a time (rename, extract, move, shorten). Do not mix refactoring with new behavior.
4. When shortening, verify behavior is identical — the tests must pass unchanged. Never trade functionality for brevity.
5. Check that module independence (8.2), the config schema (8.6) and the output layout (8.5) still hold after moving code.
6. Run tests and Ruff after each step, not only at the end.

## 10. Testing

- Test runner: `pytest`, configured in `pyproject.toml`. Tests live in `tests/` and mirror the package structure one-to-one.
- Every module ships with a test. No exceptions.
- Test modules with small synthetic inputs built in the test, with variable names that differ from any real dataset, to prove the module is data-agnostic.
- Test `load_config` with a valid YAML, a YAML with an unknown key, a YAML missing a required key and a YAML with an out-of-range value.
- Test that every YAML in `config/` loads into its module's `Config`.
- Use `tmp_path` for anything that touches files; assert the output layout (8.5) is produced correctly.
- A bug fix includes a regression test that fails before the fix and passes after.
- Run before finishing any task:
  ```bash
  pytest -q
  ```

## 11. Done checklist

Do not report a task as complete until every item is verified:

- [ ] Each module has its own YAML in `config/`, named after the module, and runs standalone with `--config`.
- [ ] No global config file, no `enabled` flags, no CLI flags that change scientific behavior.
- [ ] No registry, base class, factory, plugin system or wrapper indirection anywhere.
- [ ] No module imports another module; shared code is generic only and lives in `common.py`.
- [ ] `run()` reads as load → validate → process → write, in one screen.
- [ ] Every function has full type annotations.
- [ ] No `print()`; all output goes through `logging`.
- [ ] No bare `except:` or swallowed exceptions.
- [ ] No hardcoded column/variable names, units, IDs or schemas anywhere in `src/`.
- [ ] No magic numbers; every parameter is in the module's YAML and validated in `load_config`.
- [ ] No redundant lines: no one-line wrappers, no single-use temporaries, no duplicated logic, no dead code or unused parameters.
- [ ] Every shortened block is still obvious to read; no functionality was lost.
- [ ] Outputs are written flat into that module's `output_dir`, with `run.log` and `config.used.yaml`.
- [ ] New modules are added to `scripts/run_all.py` `STEPS` and to `README.md` in run order.
- [ ] `pyproject.toml` is the only build/tool config file.
- [ ] `ruff check --fix . && ruff format .` runs clean.
- [ ] `pytest -q` passes, and new code has tests.
- [ ] `main()` returns an exit code, accepts an optional config path, and is called via `sys.exit(main())`.
- [ ] Focused change: nothing unrelated was edited.
