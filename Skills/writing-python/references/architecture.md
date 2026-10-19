# Codebase architecture

Read when creating a module, a config file, the runner, or an output directory.

## Layout

Use this structure exactly. Create a missing directory when adding the first file that belongs there; never invent an alternative layout.

```
project/
├── pyproject.toml           # REQUIRED: dependencies, ruff, pytest. No setup.py, requirements.txt or ruff.toml.
├── README.md                # each module in run order, with its input, output and config file
├── config/
│   ├── extract_features.yaml    # one YAML per module, named after the module
│   └── filter_cells.yaml
├── notebooks/               # exploration only; imports from src/, holds no logic a module depends on
├── scripts/
│   └── run_all.py           # thin runner: calls each module's main() in a literal fixed order
├── src/<package>/
│   ├── __init__.py
│   ├── errors.py            # PipelineError, ConfigError, DataError
│   ├── common.py            # prepare_output_dir, dump_config_used — generic only
│   ├── extract_features.py  # standalone module
│   └── filter_cells.py
└── tests/                   # mirrors src/<package>/ one-to-one
```

- Modules live flat in `src/<package>/`. No `processing/`, `analysis/`, `visualization/` sub-packages.
- Data and outputs live wherever the user's YAML points, never inside the repository unless the user chooses so.

## Config schema

One YAML per module in `config/`, named after the module. `Config.from_yaml` reads it, rejecting unknown keys, missing required keys and out-of-range values with a `ConfigError` naming the key.

```yaml
# config/filter_cells.yaml
input_path: /data/experiment_01/features.csv
output_dir: /results/experiment_01/filter_cells

log_level: INFO
seed: 42

variables: [area, intensity_mean]   # must exist in the input file
method: iqr                         # iqr | zscore
factor: 1.5
```

- Flat by default. Nest only when a group genuinely belongs together. No `stages:` tree, no per-method sub-blocks, no `enabled` flags.
- A config contains only keys its module reads. A key nobody reads is a bug.
- Committed with working defaults and a one-line comment per parameter; it is the documentation of what the module can do.
- Keys map one-to-one onto `Config` fields. A test loads every YAML in `config/` into its module's `Config`.
- `from_yaml` cannot check variable names (data not loaded yet); `run()` validates them against the loaded data before processing.

## Data-agnostic loading

- Loaders return a frozen dataclass holding the data plus the metadata discovered: variable names, units if present, sample identifiers, source path.
- Loaders infer schema from the file (headers, index, attributes). They never take a hardcoded list of expected columns.

## Output directory

Each module writes flat into its own `output_dir` from the YAML:

```
<output_dir>/
├── run.log                  # this run's log
├── config.used.yaml         # the exact config used, defaults filled in
├── <result>.csv
└── <figure>.png
```

- One level, no nesting. Plain names: `filtered_cells.csv`, not `fc_v2_final.csv`.
- A module writes only inside its own `output_dir` — never into the input directory or another module's output.
- `common.py` owns directory creation and the `config.used.yaml` dump, one function each.
- Chaining is explicit: the user sets the next module's `input_path` to a file in the previous `output_dir`.

## The runner

`scripts/run_all.py` is the only place that knows the full order:

```python
from pathlib import Path
import sys

from mypackage import extract_features, filter_cells

CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"

STEPS = [
    (extract_features.main, "extract_features.yaml"),
    (filter_cells.main, "filter_cells.yaml"),
]


def main() -> int:
    for step, config_name in STEPS:
        code = step(CONFIG_DIR / config_name)
        if code != 0:
            return code
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- No processing logic, no config parsing, no conditionals beyond the failure check. Stops at the first non-zero code.
- Adding a module means adding one line to `STEPS`.
- The runner is optional convenience; every module still works alone.

## Notebooks

- Exploration and reporting only. They import from `src/<package>/`.
- Logic that becomes reusable moves into a module with a test.
