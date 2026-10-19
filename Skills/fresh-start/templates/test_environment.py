"""The declared environment agrees with pyproject.toml, and carries the gates.

A gate tool missing from the environment does not fail: `importorskip`
turns the docstring check into a skip and the run stays green. These tests
make the absence fail instead, and pin the one value `environment.yml`
duplicates from `pyproject.toml` — the Python version — so the two files
cannot disagree.
"""

from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent

if sys.version_info >= (3, 11):
    import tomllib
else:
    tomllib = pytest.importorskip("tomli")

#: Every tool a phase gate runs. One missing means a gate silently did not run.
GATE_TOOLS = ("pytest", "ruff", "numpydoc", "build", "twine")


def test_every_gate_tool_is_importable_here() -> None:
    """Fail when the environment running the suite lacks a gate tool.

    Returns
    -------
    None
        The assertion is the test's only effect.
    """
    missing = [name for name in GATE_TOOLS if importlib.util.find_spec(name) is None]
    assert not missing, (
        f"gate tools missing from this environment: {missing}; run `pip install -e .[dev]`"
    )


def test_environment_file_installs_the_dev_extra() -> None:
    """Fail when `environment.yml` stops installing `.[dev]`.

    Listing the dev tools by name in both files is the drift this guards
    against; the environment file must defer to `pyproject.toml`.

    Returns
    -------
    None
        The assertion is the test's only effect.
    """
    text = (ROOT / "environment.yml").read_text()
    assert ".[dev]" in text, "environment.yml must install the package with `-e .[dev]`"


def test_environment_python_matches_requires_python() -> None:
    """Fail when `environment.yml` pins a Python older than `requires-python`.

    Returns
    -------
    None
        The assertion is the test's only effect.
    """
    with (ROOT / "pyproject.toml").open("rb") as handle:
        requires = tomllib.load(handle)["project"]["requires-python"]
    minimum = re.search(r"(\d+\.\d+)", requires).group(1)

    env_text = (ROOT / "environment.yml").read_text()
    pinned = re.search(r"python\s*=\s*(\d+\.\d+)", env_text)
    assert pinned, "environment.yml must pin `python=X.Y`"
    assert tuple(map(int, pinned.group(1).split("."))) >= tuple(map(int, minimum.split("."))), (
        f"environment.yml pins python={pinned.group(1)} but pyproject requires {requires}"
    )
