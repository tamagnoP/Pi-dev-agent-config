# PACKAGE_NAME — task tracker

The single source of truth for what is done, what is running and what is next.
Updated the moment a task completes, not at the end of a session.

A completed task carries its EVIDENCE, not just a tick: the test count, the
wall time, the number that settled it, the path to the log. "Done" with no
number attached is a claim nobody can check later.

## The version ladder

`0.0.1` reserves the name and promises nothing. The version climbs as each
piece lands and is proven, and reaches `1.0.0` only when the whole thing runs
end to end. Each step up requires: tests passing, ruff zero, docs build clean,
`CHANGELOG.md` entry written, then `git tag vX.Y.Z`.

| version | means | status |
|---|---|---|
| 0.0.1 | name reserved, no functionality | |
| 0.1.0 | FIRST SUBSYSTEM works, with tests and a real-input check | |
| 1.0.0 | end to end, documented, released | |

## Bootstrap

- [ ] 1  `git init`; `.gitignore` is commit #1
- [ ] 2  `pip install -e .` works; no console script declared before its module
- [ ] 3  `environment.yml` exists; `pip check` clean; `tests/test_environment.py` passes
- [ ] 4  `pytest -q` passes, including a test for a refusal
- [ ] 5  `ruff check src tests` and `ruff format --check src tests` -> 0
- [ ] 6  `python scripts/validate_docstrings.py` -> 0, enforced by the suite
- [ ] 7  `cd docs && make strict` -> build succeeded, 0 warnings
- [ ] 8  CI green: `ci.yml` and `docs.yml`, both required by branch protection
- [ ] 9  `.readthedocs.yaml` committed and inert; build measured against limits
- [ ] 10 `CHANGELOG.md` entry for the declared version; `tests/test_changelog_version.py` passes
- [ ] 11 `TODO.md`, `DECISIONS.md`, `option-testing/` exist
- [ ] 12 built wheel installs and imports in a clean environment

## In progress

## Next

## Open questions

Things known and not blocking. Each one says what is unknown and what would
settle it.
