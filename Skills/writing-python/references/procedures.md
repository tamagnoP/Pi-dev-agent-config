# Change procedures and testing

Read when adding, deleting or refactoring a module or feature, and when writing tests.

## Adding a module

1. Search `src/` first; confirm no existing module already does this.
2. Create `src/<package>/<module>.py` following the module anatomy in SKILL.md.
3. Create `config/<module>.yaml` with every parameter, working defaults and one-line comments.
4. Add one line to `STEPS` in `scripts/run_all.py`, in the correct position.
5. Add `tests/test_<module>.py` covering normal input, a missing-variable failure and a bad-config failure.
6. Add the module to `README.md` in run order, stating its input and output.
7. Do not touch other modules. If you had to, module independence is being violated — stop and ask.

## Adding a feature to a module

1. Confirm it belongs to that module's one job. If describing it needs an "and", it is a new module — ask the user.
2. Add its parameters to `Config`, `from_yaml` validation and `config/<module>.yaml`.
3. Keep `run()` on one screen; if it no longer fits, extract a named work function — not a new layer.
4. Add tests for the new behaviour.

## Deleting a module or feature

1. Find every reference: `grep -rn "<name>" src/ tests/ scripts/ notebooks/ config/`.
2. List the affected files to the user before deleting anything.
3. Check whether any other module's YAML uses its `output_dir` as `input_path`. If so, stop and ask: that chain breaks.
4. Remove the code, its tests, its `config/<module>.yaml`, its `STEPS` line and its `README.md` entry.
5. Make `from_yaml` reject the removed keys so stale user YAMLs fail loudly.
6. Remove now-unused imports and helpers (`ruff check` flags them).
7. Run the full test suite. Deletion is complete only when it passes.

## Refactoring

1. Ask the user for scope (full codebase or a directory). Stay inside it.
2. Run the test suite first. If tests are missing for the code being refactored, write characterization tests that capture current behaviour before changing anything.
3. One kind of change at a time (rename, extract, move, shorten). No new behaviour mixed in.
4. When shortening, tests must pass unchanged. Never trade functionality for brevity.
5. Re-check module independence, the config schema and the output layout after moving code.
6. Run tests and Ruff after each step, not only at the end.

## Testing

- `pytest`, configured in `pyproject.toml`. Tests in `tests/`, mirroring the package one-to-one.
- Every module ships with a test. No exceptions.
- Build small synthetic inputs in the test, with variable names that differ from any real dataset, to prove the module is data-agnostic.
- Test `from_yaml` with: a valid YAML, an unknown key, a missing required key, an out-of-range value.
- Test that every YAML in `config/` loads into its module's `Config`.
- Use `tmp_path` for anything touching files; assert the output layout (`run.log`, `config.used.yaml`, results) is produced.
- A bug fix includes a regression test that fails before the fix and passes after.
- Run `pytest -q` before finishing any task.
