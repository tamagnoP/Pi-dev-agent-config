# Style and execution rules

Read when writing or editing Python. Complements the non-negotiables in SKILL.md.

## Execution structure

- Every module is a script with one job. All execution logic lives in `main()`; nothing executes at global scope.
- `main()` returns an exit code; `sys.exit` appears only in the guard block. This keeps `main()` testable and callable by the runner.
- `main()` accepts an optional config path so `scripts/run_all.py` can call it directly instead of shelling out.
- Return `0` on success, non-zero on any fatal error. Shell pipelines and CI depend on these codes.

```python
def main(config_path: Path | None = None) -> int:
    path = config_path or parse_args().config
    config = Config.from_yaml(path)
    output_dir = prepare_output_dir(config.output_dir)
    logging.basicConfig(
        level=config.log_level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[logging.StreamHandler(), logging.FileHandler(output_dir / "run.log")],
    )
    try:
        run(config)
    except PipelineError as exc:
        logger.error("%s failed: %s", MODULE_NAME, exc)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

## Command-line arguments

- `argparse` in a dedicated `parse_args()`. Never index `sys.argv`.
- Every argument has a `type`, a `help` string, and `required=True` when it is.
- `--config` (required, `type=Path`); optionally `--dry-run` and `--verbose`. Nothing else.
- `parse_args()` only collects arguments. No processing logic in it.

## Paths

- `pathlib.Path` for every path. No string concatenation, no `os.path`.
- Project-relative paths are anchored to the file: `BASE_DIR = Path(__file__).resolve().parent`.
- Input and output locations come from the YAML, never from literals in processing code.

## Logging

- Configure logging exactly once, in `main()`, via `logging.basicConfig(...)` with a console handler and a file handler writing `<output_dir>/run.log`.
- Each module has its own `logger = logging.getLogger(__name__)` at the top. Never call the root logger from processing code.
- Levels: `debug` for traces and intermediate values; `info` for module start/end and progress; `warning` for non-fatal problems, retries, fallbacks; `error` for failures.
- At run start, log the module name, the input path and the resolved configuration.

## Types and errors

- PEP 8. Annotate every parameter and return. `int | None`, not `Optional[int]`.
- Config and loaded data are `@dataclass(frozen=True)`, flat, fields only. The one allowed method is `Config.from_yaml`.
- Wrap external interactions (file I/O, network, subprocess) in `try/except` that catches specific exceptions, logs a concrete message, and exits non-zero. Silent failures are worse than crashes.
- `errors.py` holds the whole hierarchy:
  ```python
  class PipelineError(Exception): ...
  class ConfigError(PipelineError): ...   # bad or missing YAML values
  class DataError(PipelineError): ...     # variable not in input, wrong shape, bad values
  ```

## Code style

- **Names reveal intent.** No abbreviations, no single-letter names.
- **Small functions, flat logic.** Guard clauses and early returns over nested `if`. One level of abstraction per function.
- **Write it once, write it short.** Comprehensions over accumulator loops; direct returns over single-use temporaries; stdlib/pandas/numpy built-ins over hand-rolled loops. Stop the moment it stops being obvious.
- **Cut the ceremony.** No getters/setters, no one-line wrappers that only call another function, no re-validation of values already validated in `from_yaml`, no dead parameters, no "for later" hooks.
- **One change per change.** Don't mix a refactor with new behaviour.
- **Comments explain decisions**, not what the code already says. Docstrings: see `docstrings.md`.
- **Don't pessimize.** Avoid obvious waste (whole-file loads when streaming works, quadratic loops over large data), but never add complexity for speculative speed.
- **Formatting is automated.** Ruff lints and formats, configured in `pyproject.toml`: `ruff check --fix . && ruff format .`

## Design principles

- **KISS.** The most straightforward design that works. Complexity only when a real constraint demands it.
- **Directness over indirection.** Call the function. If a reader must jump through two files to find what runs, the design is wrong.
- **DRY.** Each piece of knowledge lives in one place; for parameters, that place is the YAML.
- **One module, one job.** If describing a module needs an "and", split it.
- **Modules communicate through files on disk only.** One module's `output_dir` is the next module's `input_path`, set by the user.
- **Shared code is small and dumb.** `common.py` holds only generic helpers (output-directory creation, `config.used.yaml` dump). No domain knowledge, no branching on module names.
- **Decisions in pure functions, side effects at the edges.**
- **Design for failure.** Expect missing files, missing variables, bad input. Every failure message is one a human can act on.
