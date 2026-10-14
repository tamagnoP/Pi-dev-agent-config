"""Check every public docstring in `src/` against the numpydoc schema.

A docstring convention is a preference until something fails on a breach: a
Google-style heading or a missing `Returns` section otherwise passes every
test. This script is that enforcement. It is import-based rather than
Sphinx-based, so it runs in seconds and needs no documentation build; the
documentation build is a separate gate covering whether the docstrings render.

Three checks are excluded from the default set, and that exclusion is the
reason this file exists rather than a bare `numpydoc.validate` call:

* `SA01` and `EX01` require a `See Also` and an `Examples` section on every
  object. A codebase that does not write those sections can never clear them.
* `ES01` requires an extended summary. It fires on one-line docstrings that
  are already complete, where a second paragraph would be padding.

If the project does write See Also or Examples sections, remove the relevant
code from `EXCLUDED_CHECKS` below rather than leaving a rule unenforced.

`Enum` subclasses and `typing.Protocol` classes are excluded as objects, not as
checks. numpydoc inspects the metaclass signature for an Enum and reports
`module`, `names`, `start`, `value`, `qualname` and `type` as undocumented
parameters; they belong to the functional Enum API, not to the class, and no
docstring can document them.
"""

from __future__ import annotations

import argparse
import enum
import importlib
import inspect
import pkgutil
import typing

#: Checks that can never pass on this codebase; see the module docstring.
EXCLUDED_CHECKS = frozenset({"SA01", "EX01", "ES01"})


def importable_modules(package: object) -> tuple[list[object], list[str]]:
    """Import every submodule of `package`, reporting those that refuse.

    A module whose optional dependency is absent is SKIPPED and named rather
    than failing the run: `fitting/plotting/*` needs `pyvista`, which the core
    install does not carry, and a checker that fails on a missing extra would
    be a checker nobody runs.

    Parameters
    ----------
    package : object
        The imported top-level package.

    Returns
    -------
    tuple[list[object], list[str]]
        The imported modules, and the dotted names that could not be imported.
    """
    modules, skipped = [], []
    for found in pkgutil.walk_packages(package.__path__, package.__name__ + "."):
        try:
            modules.append(importlib.import_module(found.name))
        except Exception as exc:          # any import error is a skip, not a failure
            skipped.append(f"{found.name} ({type(exc).__name__}: {exc})")
    modules.append(package)
    return modules, skipped


def is_excluded_object(obj: object) -> bool:
    """Report whether numpydoc cannot meaningfully validate this object.

    Parameters
    ----------
    obj : object
        A class or function found in a module namespace.

    Returns
    -------
    bool
        True for `Enum` subclasses and `Protocol` classes, whose reported
        parameters come from the metaclass rather than from the declaration.
    """
    if not inspect.isclass(obj):
        return False
    if issubclass(obj, enum.Enum):
        return True
    return bool(getattr(obj, "_is_protocol", False)) or obj is typing.Protocol


def public_targets(modules: list[object]) -> set[str]:
    """Collect the dotted names of every public object worth validating.

    Public functions and classes defined IN the module, plus their public
    methods. `__module__` is checked so a re-export is validated once, where it
    is defined, instead of once per module that imports it.

    Parameters
    ----------
    modules : list[object]
        The imported modules.

    Returns
    -------
    set[str]
        Dotted names `numpydoc.validate.validate` can resolve.
    """
    targets: set[str] = set()
    for module in modules:
        for name, obj in vars(module).items():
            if name.startswith("_"):
                continue
            if not (inspect.isfunction(obj) or inspect.isclass(obj)):
                continue
            if getattr(obj, "__module__", None) != module.__name__:
                continue
            if is_excluded_object(obj):
                continue
            targets.add(f"{module.__name__}.{name}")
            if inspect.isclass(obj):
                for method_name, method in vars(obj).items():
                    if method_name.startswith("_"):
                        continue
                    if inspect.isfunction(method) or isinstance(method, property):
                        targets.add(f"{module.__name__}.{name}.{method_name}")
    return targets


def violations(targets: set[str]) -> dict[str, list[tuple[str, str]]]:
    """Validate each target and keep only the checks that are enforced here.

    Parameters
    ----------
    targets : set[str]
        Dotted names to validate.

    Returns
    -------
    dict[str, list[tuple[str, str]]]
        Dotted name to its (code, message) violations, objects with none
        omitted.
    """
    from numpydoc.validate import validate

    found: dict[str, list[tuple[str, str]]] = {}
    for target in sorted(targets):
        try:
            report = validate(target)
        except Exception:                 # an unresolvable name is not a violation
            continue
        errors = [(code, msg) for code, msg in report["errors"] if code not in EXCLUDED_CHECKS]
        if errors:
            found[target] = errors
    return found


def main(argv: list[str] | None = None) -> int:
    """Validate the package and report every violation found.

    Parameters
    ----------
    argv : list[str] or None, optional
        Argument list; None reads `sys.argv`.

    Returns
    -------
    int
        0 when every public docstring passes, 1 otherwise.
    """
    parser = argparse.ArgumentParser(
        description="Check public docstrings against the numpydoc schema."
    )
    parser.add_argument("--quiet", action="store_true", help="print only the totals")
    args = parser.parse_args(argv)

    import PACKAGE_NAME

    modules, skipped = importable_modules(PACKAGE_NAME)
    targets = public_targets(modules)
    found = violations(targets)

    total = sum(len(v) for v in found.values())
    if not args.quiet:
        for target, errors in found.items():
            print(target)
            for code, message in errors:
                print(f"    {code}  {message}")
        if found:
            print()
    print(f"{len(targets)} objects checked across {len(modules)} modules")
    if skipped:
        print(f"{len(skipped)} module(s) skipped (optional dependency absent):")
        for name in skipped:
            print(f"    {name}")
    print(f"{total} violation(s) in {len(found)} object(s)")
    return 1 if total else 0


if __name__ == "__main__":
    raise SystemExit(main())
