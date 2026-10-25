# Ambiguity Protocol — tested options

Read this file only when triggered by rule 2 of APPEND_SYSTEM.md: the request is ambiguous, the plausible paths are technical, and they can only be compared by running them.

## Step 1 — Test every path
- Run real tests for each plausible path. Every option presented must be backed by its own result. Purely theoretical options are not allowed.
- Each option gets its own isolated directory: `option-testing/[DECISION-ID]_isolated_tests/`, where `option-testing/` sits in the same root directory as `TODO.md`. Create it if missing.
- Write all logs, outputs, and findings as `.md` inside that directory, following the template at `/Users/Office/.pi/agent/templates/TEST_TEMPLATE.md` exactly.

## Step 2 — Log in DECISIONS.md
- Before replying, record every tested option and its empirical result in `DECISIONS.md` (project root).
- Follow the template at `/Users/Office/.pi/agent/templates/DECISIONS_TEMPLATE.md` exactly, whether creating or appending.

## Step 3 — Halt and present
Stop execution. Present the options as a numbered list. For each option give:
- What the path entails.
- The primary trade-off, benefit, or risk.
- The test result that supports it.

Then explicitly ask the user to choose or to provide clarifying details.

## Step 4 — After the user chooses
- Update `DECISIONS.md` to mark the chosen option.
- State, in plain English, why it was chosen and how it will be implemented.
- Only then proceed to production code.
