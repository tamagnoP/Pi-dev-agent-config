# Docstrings — numpydoc, checked by the validator

Read before writing or rewriting any docstring. Shared by `writing-python` and `refactor-python`.

## Why numpydoc, not Google style

Sphinx with the `numpydoc` extension (the Read the Docs toolchain for these projects) parses only hyphen-underlined sections. A Google-style `Parameters:` / `Args:` block is swallowed into the description as prose, and the validator then reports a documented function as undocumented (`PR01`, `RT01`). Converting Google style to numpydoc is a fix, not a preference.

## Form

- PEP 257: triple double-quotes, one-line summary, blank line, body.
- **Summary**: one line, infinitive (`Compute ...`, never `Computes ...` or `Indices of ...`), ends with a full stop, does not repeat the function name.
- **Mechanism and reasoning go below the summary**, in the extended summary — or in `Notes` when they are background theory or a derivation. A docstring that only restates the return value is the anti-pattern.
- **Headings** are underlined with hyphens of matching length, no colon: `Parameters` / `----------`.
- **Entries** are `name : type` (space before the colon), description indented four spaces on the next line. Never `name (type): text`.
- **Section order** is fixed: summary, extended summary, `Parameters`, `Returns` (or `Yields`), `Raises`, `See Also`, `Notes`, `References`, `Examples`. `Raises` before `Returns` is a `GL07` failure.
- Parameter names elsewhere in the docstring go in single backticks.
- Lines wrap at 75 characters.

Every function and class docstring has `Parameters` and `Returns`. Add `Raises` whenever a function can raise `ConfigError` or `DataError` — in this architecture that contract always qualifies.

## Write to the checker

`numpydoc.validate` is the arbiter. These are the checks that actually fire:

| check | rule |
|---|---|
| `PR01` | every signature parameter appears in `Parameters`, nothing else does |
| `PR02` | no stray punctuation in a name — `x,` is a different parameter |
| `PR03` | `Parameters` in signature order, not importance order |
| `PR04` | every entry has a type |
| `PR07` | every entry has a description on the next line |
| `PR08` / `PR09` | description starts with a capital, ends with a full stop |
| `RT01` | a `Returns` section always, including for `None` |
| `RT02` | first line of `Returns` is the type alone; `lag : np.ndarray` fails |
| `RT03` / `RT04` | the description exists and starts with a capital |
| `SS03` | summary ends with a full stop |
| `SS05` | summary is an infinitive |
| `SS06` | summary fits on one line |
| `GL06` | only numpydoc section names; an invented heading's content is dropped from the rendered page |
| `GL07` | sections in the fixed order |

- **Never invent a heading.** `Components`, `WHAT IS NOT HERE` → `GL06`. Put that prose in `Notes` with a bold run-in lead (`**The three components.**`) instead.
- **No grouped parameters.** `x, y : int` is tolerated for two same-typed names; `a, b, c : int` with one shared description fails `PR04`/`PR07` on every name. Document each separately.
- **Three checks are excluded by policy; never write to satisfy them**: `SA01` (See Also), `EX01` (Examples), `ES01` (extended summary on an already-complete one-liner). Enforce `{'all'} - {SA01, EX01, ES01}`.
- **Skip `Enum` subclasses and `typing.Protocol` classes as objects.** numpydoc reads the Enum metaclass signature and reports `module`, `names`, `start`, `value`, `qualname`, `type` as undocumented. That `PR01` is a false positive.

Before finishing, run the checker rather than re-reading:

```bash
python scripts/validate_docstrings.py
```

If the project has no checker: `python -m numpydoc.hooks.validate_docstrings <module>`.

## Example

```python
def bootstrap_delta_ci(
    reference: np.ndarray,
    test: np.ndarray,
    scale: str,
    n_bootstrap: int,
    seed: int,
    alpha: float,
) -> tuple[float, float]:
    """Compute a percentile bootstrap CI for the difference of two means.

    Resamples within each group separately rather than across both, which
    lets the interval reflect replicate spread without assuming a shared
    variance. With 'log2fc' an iteration is dropped when either resampled
    mean is non-positive, because the ratio is undefined there. The
    generator is seeded, so a rerun reproduces the interval exactly.

    Parameters
    ----------
    reference : np.ndarray
        Control group values; NaN entries are dropped.
    test : np.ndarray
        Treated group values; NaN entries are dropped.
    scale : str
        'log2fc' for a ratio, anything else for a plain difference.
    n_bootstrap : int
        Number of resampling iterations.
    seed : int
        Seed for the random generator, making the interval reproducible.
    alpha : float
        Two-sided level; the interval spans the alpha/2 percentiles.

    Returns
    -------
    tuple[float, float]
        (ci_lower, ci_upper), or (nan, nan) when either group has fewer
        than two finite values or every iteration was undefined.
    """
```

## Specific cases

- **Returns `None`**: still write `Returns`, naming the side effect:
  ```
  Returns
  -------
  None
      The file is written as a side effect.
  ```
- **Generators**: `Yields` instead of `Returns`, same form; type required, name optional.
- **`Config` dataclasses**: document every field under `Parameters`, in declaration order, phrased against the YAML key the user edits.
- **Exception classes**: document the constructor argument:
  ```
  Parameters
  ----------
  *args : object
      Forwarded to Exception; a message naming the file and the offending columns.
  ```
  Keep the star; give no type for `**kwargs`.
- **Module docstrings**: no sections — one paragraph on purpose, one on approach.
- **Fixed-value parameters**: options in braces, default first: `order : {'C', 'F', 'A'}`.
- **Optional parameters**: `x : int, optional`, or `copy : bool, default True`.
- The type in the section is for the reader; the description carries the information. Don't restate the annotation as a substitute for explaining the purpose.
