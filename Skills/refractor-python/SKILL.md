---
name: refractor-python
description: Performs a rigorous post-development cleanup of Python codebases. Runs a deep architecture sync, identifies and purges dead or stale code with zero tolerance, and refactors all inline documentation into PEP 8-compliant, mechanics-driven docstrings (explaining 'how' and 'why' instead of just results) complete with typed Parameters and Returns sections. Operates behind an interactive user approval gate and runs safety verification tests before finalizing the repository knowledge graph.
---

# Execution Workflow (Strict Phase Gates)

## Phase 1: Force Initial Graph Synchronization
Before doing any analysis, you MUST sync the repository map to ensure you are analyzing the latest state of the files by executing:
`/graphify path/to/root/dir-of-the-project --update --mode deep`

## Phase 2: Architectural Ingestion & Scan
Read the latest state of the `graphify-output` file (JSON/Text map). Identify:
- All dead code (variables, functions, classes, or imports with ZERO inbound edges).
- All stale code (commented-out blocks, outdated markers).
- Violations of the "How/Why" documentation rule, PEP 8, and structural Params/Returns requirements.

## Phase 3: The Interactive Gate (Stop & Report)
**CRITICAL:** You are NOT allowed to modify any file yet. You must halt and output all findings to the user.
- Present a detailed summary of dead/stale code found.
- Show a preview or side-by-side diff of the proposed docstring rewrites.
- **Explicitly wait for user approval.** Do not proceed until the user gives confirmation to apply the fixes.

## Phase 4: Execution & Verification Testing
Once approved, apply the modifications to the codebase. Immediately after modifying:
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

## 3. Python Docstring Transformation (PEP 8, Full Schema & The "How/Why" Rule)
Audit every single comment and docstring. Every docstring must comply with **PEP 8 guidelines** (triple double-quotes `"""`, concise summary, proper spacing) and follow the explanatory rule.

**Docstring Structural Requirements:**
Each docstring MUST include explicit sections for **Parameters** and **Returns**, mapping out the types and purpose of each.
- **ANTI-PATTERN (Fix):** Docstrings that merely state the result in plain English (e.g., `"""Returns the reversed String."""`).
- **CORRECT PATTERN (Apply):** The main description must explain *how* the code works or *why* that approach was used, followed by the structured Parameters and Returns.

*Example of a Refactored Function:*
```python
def string_reverse(str1: str) -> str:
    """
    Utilizes Python's negative step slicing mechanism ([::-1]) to efficiently 
    reverse the sequence of characters in memory without allocating manual loop buffers.

    Parameters:
        str1 (str): The target string that needs to be inverted.

    Returns:
        str: A new string instance containing the characters of str1 in reverse order.
    """
    return str1[::-1]
```

# Output Structure (Phase 3 Report)
When presenting findings to the user before proceeding, use this exact structure:
1. **Graph Sync Status:** Confirmation of the initial deep sync.
2. **Dead & Stale Code Report:** Bulleted list of candidates for deletion (including cascade warnings).
3. **PEP 8 & "How/Why" Docstring Diff:** Before/After text blocks of proposed documentation upgrades.
4. **Prompt for Approval:** A direct question asking the user for permission to execute.
