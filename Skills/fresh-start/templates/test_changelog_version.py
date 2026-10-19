"""The changelog has an entry for the version the package declares.

A version bump without a changelog entry is the reconstruction the changelog
header warns against. This test makes the omission fail the suite instead of
being noticed at release time.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent

if sys.version_info >= (3, 11):
    import tomllib
else:
    tomllib = pytest.importorskip("tomli")


def test_changelog_has_an_entry_for_the_declared_version() -> None:
    """Fail when `CHANGELOG.md` lacks a `## [X.Y.Z]` heading for the version.

    Returns
    -------
    None
        The assertion is the test's only effect.
    """
    with (ROOT / "pyproject.toml").open("rb") as handle:
        version = tomllib.load(handle)["project"]["version"]

    changelog = (ROOT / "CHANGELOG.md").read_text()
    heading = re.compile(rf"^## \[{re.escape(version)}\]", re.MULTILINE)
    assert heading.search(changelog), (
        f"CHANGELOG.md has no `## [{version}]` entry for the version in pyproject.toml"
    )
