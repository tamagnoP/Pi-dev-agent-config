# Done checklist

Read before reporting any task as complete. Verify every item; do not tick from memory.

**Architecture**
- [ ] Each module has its own YAML in `config/`, named after it, and runs standalone with `--config`.
- [ ] No global config, no `enabled` flags, no CLI flag that changes scientific behaviour.
- [ ] No registry, base class, factory, plugin system or wrapper indirection anywhere.
- [ ] No module imports another module; `common.py` is generic only.
- [ ] `run()` reads as load → validate → process → write, on one screen.
- [ ] Outputs written flat into the module's `output_dir`, with `run.log` and `config.used.yaml`.
- [ ] New modules added to `STEPS` in `scripts/run_all.py` and to `README.md` in run order.
- [ ] `pyproject.toml` is the only build/tool config file.

**Code**
- [ ] `main()` returns an exit code, accepts an optional config path, is called via `sys.exit(main())`, and configures logging once with `basicConfig`.
- [ ] Every function fully type-annotated.
- [ ] No `print()`; all output through `logging`.
- [ ] No bare `except:` or swallowed exceptions.
- [ ] No hardcoded column/variable names, units, IDs or schemas in `src/`.
- [ ] No magic numbers; every parameter is in the YAML and validated in `from_yaml`.
- [ ] No one-line wrappers, single-use temporaries, duplicated logic, dead code or unused parameters.
- [ ] Every shortened block is still obvious; no functionality lost.
- [ ] Nothing unrelated was edited.

**Docstrings**
- [ ] Every function, class and module has a docstring whose body explains the mechanism or the reason, not just the result.
- [ ] Every function and class docstring has numpydoc `Parameters` and `Returns`, plus `Raises` where `ConfigError`/`DataError` is part of the contract.
- [ ] No colon-terminated `Parameters:` / `Args:` headings anywhere.
- [ ] Every `Config` field documented in declaration order against its YAML key.
- [ ] `python scripts/validate_docstrings.py` reports nothing for new or edited objects.

**Checks**
- [ ] `ruff check --fix . && ruff format .` runs clean.
- [ ] `pytest -q` passes; new code has tests.
