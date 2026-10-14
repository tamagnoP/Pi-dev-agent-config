"""Sphinx configuration.

This build exists to prove what an import-based docstring checker cannot: that
the docstrings RENDER. The schema is validated by the test suite in ~10 s with
no Sphinx at all; what it cannot see is a block quote that ends without a blank
line, a definition list that unindents too early, or a title underline one
character short. This build can, and `-W` makes each one a failure.

The package is IMPORTED, not parsed, so the documentation environment must be
able to import every module. Install the full extras: a module that cannot be
imported is not documented, and an undocumented module cannot fail a build.
"""

from __future__ import annotations

import sys
from importlib import metadata
from pathlib import Path

# The build normally runs against the installed package; the path is inserted
# so a plain `sphinx-build docs docs/_build` also works in a fresh checkout.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

project = "PACKAGE_NAME"
author = "AUTHOR"
copyright = "YEAR, AUTHOR"
release = metadata.version("PACKAGE_NAME")
version = release

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "numpydoc",
    "myst_parser",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# One stub page per module, generated from the recursive autosummary in
# api/index.rst, so a new module is documented without anyone listing it.
autosummary_generate = True
autodoc_member_order = "bysource"
autodoc_typehints = "description"
autodoc_default_options = {"members": True, "show-inheritance": True}

# Class members are rendered by autodoc; leaving numpydoc's own table on as
# well documents every method twice.
numpydoc_show_class_members = False
numpydoc_class_members_toctree = False
# The schema is enforced by tests/test_docstring_schema.py on every commit.
# Re-running it here would duplicate the gate and, worse, fire on the Enum and
# Protocol objects the checker deliberately excludes — numpydoc's Sphinx hook
# has no equivalent exclusion, so the two gates would disagree about "clean".
numpydoc_validation_checks = set()

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

# Prose type descriptions ("array-like", "path-like") are deliberate; checking
# them as cross-references would fail the build on correct documentation.
nitpicky = False

html_theme = "furo"
html_title = f"{project} {release}"
html_static_path = ["_static"]

myst_enable_extensions = ["colon_fence", "deflist"]
myst_heading_anchors = 3
