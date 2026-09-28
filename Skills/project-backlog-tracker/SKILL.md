---
name: project-backlog-tracker
description: Analyzes provided context, discussions, or code snippets to identify missing features, new structural ideas, and future improvements. Automatically extracts and packages these insights into an objective, future-proof, and highly scannable Markdown format designed to be appended directly into a single tracking or backlog file.
---

# Execution Workflow

## Phase 1: Context & Source Ingestion
Analyze the user's input, code repository diffs, or descriptive ideas to capture exactly what is missing, what needs optimization, or what new feature is being conceptualized.

## Phase 2: Extraction & Structuring
Extract the core technical objective, implementation strategy, and cross-project utility without adding any conversational or peripheral elements.

# Strict Response Guidelines
1. **Be Concise and Objective:** Eliminate all conversational filler, greetings, and theoretical explanations. Provide only the required execution details.
2. **Future-Proof Descriptions:** Be explicit and clear so that the user's "future self" knows exactly what the "present self" intended, allowing for easy execution or cross-project reuse later.
3. **No Redundancy:** Keep the output highly scannable, clean, and organized.

# Expected Output Format
Format your entire response using the following Markdown structure (do not wrap it in conversational text, intros, or outros):

## - [ ] [Project Name] - [Feature / Idea Name]
* **What is missing:** [Brief, functional description of what needs to be built or fixed]
* **How to implement:** [Succinct, step-by-step technical implementation path, files to modify, or logic to use]
* **Context / Future Reuse:** [Why this matters or how this logic can be easily repurposed in other projects]
