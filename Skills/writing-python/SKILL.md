---
name: writing-python
description: Coding standards and codebase architecture for Python scientific analysis pipelines, standalone scripts and CLI utilities. Use whenever the user asks to write, extend, review or delete Python code, modules, scripts, CLI tools, data-processing steps or pipeline configuration — even if they never say "standards" or "architecture". For a full post-development cleanup pass (dead code, docstring sweep, approval gate) use refactor-python instead; it applies these standards.
---

# Python Pipeline Standards

Reference files live in `/Users/Office/.pi/agent/skills/writing-python/references/`. Read each one at the moment named below, not before.

## Workflow

| Situation | Do |
|---|---|
| Writing or editing any Python | Follow the rules on this page. Read `style.md` before writing the first function. |
| Writing or editing any docstring | Read `docstrings.md`. |
| Creating a module, config, runner or output directory | Read `architecture.md`. |
| Adding, deleting or refactoring a module or feature | Read `procedures.md`. Never skip the impact check. |
| Writing tests | Read `procedures.md` (testing section). |
| Before reporting "done" | Read `checklist.md` and verify every item. |
| Any Git command that changes state (`add`, `commit`, `push`, branches) | Tell the user first. |

## Non-negotiable rules

These override any convenience shortcut. Check them first when reviewing or writing.

1. **One module, one YAML config.** Every parameter lives in `config/<module>.yaml`. No global config, no parameters in code, environment variables, `.env` files or CLI flags. The CLI takes `--config` and, optionally, `--dry-run` / `--verbose` — never a flag that changes scientific behaviour.
2. **Every module runs standalone.** `python -m <package>.<module> --config config/<module>.yaml` works without any orchestrator. A module never imports another module; it may import `errors.py` and `common.py`.
3. **The code is data-agnostic.** Never hardcode column names, variable names, units, sample IDs, group labels, sheet names or schemas. Read them from the input at load time. Variables a module needs are named in its YAML and validated against the loaded data before processing.
4. **No abstraction layers.** No registries, plugins, `enabled` flags, base classes, inheritance, factories, dependency injection, wrappers or result-metadata objects. A module reads its config, loads its data, calls functions directly, writes outputs. The flow reads top to bottom.
5. **Every line earns its place.** If it reads clearly in 5 lines, it must not take 10. Delete clutter and ceremony — never functionality. Shorter only wins while it stays obvious.

## Module anatomy

Every module file has these five parts, in this order:

1. `logger = logging.getLogger(__name__)` and `MODULE_NAME`.
2. `@dataclass(frozen=True) class Config` with a `from_yaml(path) -> Config` classmethod that reads the YAML, rejects unknown, missing and out-of-range keys, and raises `ConfigError` naming the key.
3. Small pure work functions: take data and plain values, return data, never touch the filesystem.
4. `run(config: Config) -> None`: load → validate variables → process → write. Fits on one screen. All I/O happens here.
5. `parse_args()`, `main(config_path: Path | None = None) -> int`, `if __name__ == "__main__": sys.exit(main())`.

`main()` configures logging once with `logging.basicConfig(...)` (console plus `<output_dir>/run.log`), catches `PipelineError`, logs it, returns 1; returns 0 on success.

## Always

- `pathlib.Path` everywhere; no `os.path`, no string paths, no hardcoded absolute paths.
- `logging`, never `print()`. Log module name, input path and resolved config at run start.
- Full type annotations; `int | None`, not `Optional[int]`.
- Frozen dataclasses for config and loaded data; no loose dicts or tuples between functions.
- Catch specific exceptions. No bare `except:` or `except Exception:` that logs and continues.
- Deterministic: seeds come from the YAML, never from time.
- Failures raise `ConfigError` or `DataError` (from `errors.py`) with a message naming the module, the input and what was wrong. One `DataError` listing every missing variable, not one per variable.
- Run `ruff check --fix . && ruff format .` and `pytest -q` before finishing.
