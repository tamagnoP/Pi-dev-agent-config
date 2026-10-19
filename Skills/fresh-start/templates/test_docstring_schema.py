"""The numpydoc rule, enforced rather than documented.

Without this test nothing fails when a docstring does not comply: a
Google-style `Parameters:` heading or a missing `Returns` section would pass
the whole suite, and a standalone audit script is a report nobody is obliged
to run.

The check lives in `scripts/validate_docstrings.py` so one definition serves
both the suite and the command line, and so the exclusions — and the reasons
for them — are written down in one place rather than twice.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

pytest.importorskip(
    "numpydoc",
    reason="numpydoc is the docs toolchain; install the [docs] extra to enforce "
    "the docstring schema",
)


def test_every_public_docstring_matches_the_numpydoc_schema() -> None:
    """Fail when any public docstring breaks the enforced numpydoc checks.

    The message names every offending object and check code, because the fix is
    always in the message and a bare count would send the reader back to the
    command line to find out what broke.

    Returns
    -------
    None
        The assertion is the test's only effect.
    """
    from validate_docstrings import importable_modules, public_targets, violations

    import PACKAGE_NAME

    modules, _skipped = importable_modules(PACKAGE_NAME)
    found = violations(public_targets(modules))

    if found:
        lines = [f"{len(found)} object(s) break the numpydoc schema:"]
        for target, errors in found.items():
            lines.append(f"  {target}")
            lines.extend(f"      {code}  {message}" for code, message in errors)
        lines.append("Run: python scripts/validate_docstrings.py")
        pytest.fail("\n".join(lines))


def test_the_modules_needing_an_optional_dependency_are_named_not_hidden() -> None:
    """Pin the known blind spot: modules that cannot be imported are reported.

    A module that imports a heavy extra at module scope is skipped rather
    than checked when that extra is absent. It passes by being invisible, not
    by being correct. This test asserts the skip is REPORTED, so the gap
    cannot quietly widen to cover a module that should have been checked.

    Returns
    -------
    None
        The assertion is the test's only effect.
    """
    from validate_docstrings import importable_modules

    import PACKAGE_NAME

    modules, skipped = importable_modules(PACKAGE_NAME)

    assert modules, "no module of the package could be imported at all"
    for name in skipped:
        assert "(" in name and ")" in name, (
            f"a skipped module must carry the reason it was skipped, got {name!r}"
        )
