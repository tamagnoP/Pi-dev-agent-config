---
name: refractor-python
description: Performs a rigorous post-development cleanup of Python codebases. Runs a deep architecture sync, identifies and purges dead or stale code with zero tolerance, and refactors all inline documentation into PEP 257-compliant numpydoc (NumPy style) docstrings (explaining 'how' and 'why' instead of just results) complete with hyphen-underlined Parameters and Returns sections that render under Sphinx, numpydoc and Read the Docs. Operates behind an interactive user approval gate and runs safety verification tests before finalizing the repository knowledge graph.
---

# Execution Workflow (Strict Phase Gates)

## Phase 1: Force Initial Graph Synchronization
Before doing any analysis, you MUST sync the repository map to ensure you are analyzing the latest state of the files by executing:
`/graphify path/to/root/dir-of-the-project --update --mode deep`

## Phase 2: Architectural Ingestion & Scan
Read the latest state of the `graphify-output` file (JSON/Text map). Identify:
- All dead code (variables, functions, classes, or imports with ZERO inbound edges).
- All stale code (commented-out blocks, outdated markers).
- Violations of the "How/Why" documentation rule, PEP 8/PEP 257, and the numpydoc section requirements (hyphen-underlined `Parameters`/`Returns`, `name : type` entries, one-line infinitive summary).
- Any docstring written in Google style (`Parameters:` / `Args:` / `Returns:` with a trailing colon, or `name (type): description`). These do not render under `numpydoc` and must be converted.

## Phase 3: The Interactive Gate (Stop & Report)
**CRITICAL:** You are NOT allowed to modify any file yet. You must halt and output all findings to the user.
- Present a detailed summary of dead/stale code found.
- Show a preview or side-by-side diff of the proposed docstring rewrites.
- **Explicitly wait for user approval.** Do not proceed until the user gives confirmation to apply the fixes.

## Phase 4: Execution & Verification Testing
Once approved, apply the modifications to the codebase. Immediately after modifying:
- Validate the docstrings actually parse as numpydoc, rather than assuming they do:
  `python -m numpydoc.hooks.validate_docstrings <module>`, or a Sphinx build with
  `numpydoc_validation_checks` enabled. `PR01`, `RT01`, `SS05` or `SS06` on a function
  you just rewrote means the section syntax is still wrong.
- Run the project's test suite (e.g., via `pytest` or `unittest`).
- Thoroughly investigate any failure. If an edge case breaks or an error is introduced, revert the specific change and report it. The codebase must remain 100% functional.

## Phase 5: Final Graph Synchronization
If and only if the codebase is fully clean, functional, and completely error-free, run the sync command one last time to leave the project's knowledge graph perfectly updated:
`/graphify path/to/root/dir-of-the-project --update --mode deep`

# Core Directives & Python Standards

## 1. Dead Code Elimination (Zero Tolerance)
Using the validated reference map from `graphify-output`:
- Identify components with exactly zero inbound edges across the entire graph.
- Locate unreachable code (blocks after explicit returns/breaks).
- Pay attention to cascade effects (if removing `FuncA` leaves `FuncB` with zero references, `FuncB` must be flagged too).

## 2. Stale Code Identification
- Locate large chunks of commented-out code blocks and recommend complete removal (remind the user that Git history preserves them).

## 3. Python Docstring Transformation (numpydoc, Full Schema & The "How/Why" Rule)

**The required style is numpydoc (NumPy style), not Google style.** The whole point
of the Parameters/Returns schema is that Sphinx renders it as a typed parameter
table on Read the Docs, and the `numpydoc` extension parses ONLY the
hyphen-underlined form. A Google-style `Parameters:` block is swallowed into the
description as plain prose, and the validator then reports a fully documented
function as undocumented (`PR01 Parameters not documented`, `RT01 No Returns
section found`). Converting a Google-style docstring to numpydoc is therefore a
fix, not a preference.

Audit every single comment and docstring. Every docstring must comply with
**PEP 257** (triple double-quotes `"""`, concise summary, blank line, proper
spacing), the **numpydoc section grammar** below, and the explanatory rule.

**Docstring Structural Requirements:**
Each docstring MUST include explicit sections for **Parameters** and **Returns**,
mapping out the types and purpose of each, written as:
- A heading on its own line, **underlined with hyphens** of matching length, with
  **no trailing colon**: `Parameters` then `----------`.
- One entry per line as **`name : type`** (space before the colon), with the
  description **indented four spaces on the next line**. Never `name (type): text`.
- In `Returns`, the **type is always required**; the name is optional. Use `Yields`
  for generators.
- A **one-line summary written as an infinitive** (`Reverse ...`, not `Reverses ...`
  or `Utilizes ...`), which does not repeat the function name, then a blank line.
- Section order: short summary, extended summary, `Parameters`, `Returns`/`Yields`,
  `Raises`, `See Also`, `Notes`, `References`, `Examples`.
- Docstring lines wrapped at 75 characters.

- **ANTI-PATTERN (Fix):** Docstrings that merely state the result in plain English (e.g., `"""Returns the reversed String."""`).
- **ANTI-PATTERN (Fix):** Google-style sections — `Parameters:` / `Args:` / `Returns:` with a trailing colon, or entries written as `name (type): description`.
- **ANTI-PATTERN (Fix):** Opening with the mechanism, which leaves Sphinx with no one-line summary for index pages and sidebars.
- **CORRECT PATTERN (Apply):** A one-line infinitive summary, then the *how*/*why*
  explanation in the extended summary (or in `Notes` when it is background theory
  or a derivation), then the structured `Parameters` and `Returns` sections.

*Example of a Refactored Function:*
```python
def string_reverse(str1: str) -> str:
    """Reverse the characters of a string.

    Uses Python's negative step slicing ([::-1]), which builds the result in
    one pass at C level rather than allocating a manual loop buffer, so the
    cost stays linear and no intermediate list is created.

    Parameters
    ----------
    str1 : str
        The target string that needs to be inverted.

    Returns
    -------
    str
        A new string containing the characters of `str1` in reverse order.
    """
    return str1[::-1]
```

# Output Structure (Phase 3 Report)
When presenting findings to the user before proceeding, use this exact structure:
1. **Graph Sync Status:** Confirmation of the initial deep sync.
2. **Dead & Stale Code Report:** Bulleted list of candidates for deletion (including cascade warnings).
3. **numpydoc & "How/Why" Docstring Diff:** Before/After text blocks of proposed documentation upgrades. Flag separately any rewrite that is a Google-to-numpydoc CONVERSION rather than new content, since those change rendering, not meaning.
4. **Prompt for Approval:** A direct question asking the user for permission to execute.
