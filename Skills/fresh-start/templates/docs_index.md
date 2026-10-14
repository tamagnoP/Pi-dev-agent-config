# PACKAGE_NAME

ONE LINE: what this package does.

## What this site is

The **API reference**, generated from the source and built with `-W`, so a
docstring that does not render fails the build instead of producing a page
nobody checks.

The narrative — installation, the quick start, configuration, what each stage
expects on disk — lives in the repository `README.md`, which contributors
actually read and whose paths and commands are covered by tests.

## Documentation standard

Every docstring is NumPy style (PEP 257 + numpydoc), held to two gates that are
deliberately different:

- the test suite checks the **schema** on every commit, without Sphinx;
- this build checks that the result **renders**, which the schema check cannot
  see.

```{toctree}
:maxdepth: 2
:caption: Contents

api/index
```
