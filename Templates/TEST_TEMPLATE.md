# Instructions & Template for Option Testing

This document defines the strict directory layout, naming conventions, structural rules, and the base template for logging empirical tests within the `option-testing/` directory.

## 1. Directory Layout & Naming Conventions

**Isolated Directories:** To maintain a clean workspace, every option test must live inside its own dedicated subdirectory under `option-testing/`. This keeps logs, markdown files, and generated plots encapsulated together.

**Directory Naming Convention:** Subdirectories must be named after the decision ID.
* **Format:** `option-testing/[DECISION-ID]_isolated_tests/`
* **Example:** `option-testing/001_isolated_tests/`

**Markdown Format & File Naming:** All testing outputs, logs, parameters, and findings must be written strictly in `.md` (Markdown) format. 
* **File Format:** `test_[DECISION-ID]_[OPTION-NUMBER]_[short_descriptive_name].md`
* **Example Directory Structure:**
  ```text
  option-testing/
  └── 001_isolated_tests/
      ├── test_001_1_fastapi_endpoint.md
      ├── test_001_2_litestar_endpoint.md
      ├── performance_plot_opt1.png
      └── performance_plot_opt2.png
  ```
  
## 2. Test Document Template
*(Use the structure below when creating a new test file inside the isolated directory)*

# Test Log: [Short Descriptive Name of the Option]
**Decision ID:** `[DECISION-001]` | **Option Number:** `[Option X]`  
**Date:** YYYY-MM-DD  

### 1. Test Metadata & Environment
* **Parameters Tested:** `[e.g., batch_size=32, learning_rate=0.001, timeout=5s]`
* **Environment State:** `[e.g., Python 3.11, Ubuntu 22.04, GPU active]`
* **Total Execution Time:** `[e.g., 42.15 seconds]`

### 2. Visual Artifacts & Plotting
*(Embed any data plotting, performance curves, diagrams, or charts generated during the test here. Ensure images are stored in this same isolated directory)*

![Performance Plot or Chart](performance_plot_optX.png)
*Figure 1: Short description of what this plot demonstrates.*

### 3. Summary of Findings
**Data-Backed Conclusion:**  
[Provide a punchy, concise, data-backed conclusion summarizing why this test validates or invalidates this specific option. Use plain English.]

### 4. Raw Output & Logs
```bash
# Insert the exact terminal logs, raw output, error stack traces, or benchmark metrics here
```
