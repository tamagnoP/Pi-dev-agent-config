# My Pi personal configuration

This repository contains only my personal configuration for the Pi agent: system prompt addendum, reusable skills, and documentation templates.

I currently use this set of skills and templates for the development of research oriented data analysis workflows and pipelines implemented in Python.

[!NOTE]
**Credits:** All credit for the core system, framework, and agent logic belongs entirely to the **Pi Development Team**. This repository is solely for sharing my personal setup and how I use their tool.

## Official Repository & Tool

To find the official implementation,please visit the official project page:
* **Official Harness:** [earendil-works/pi](https://github.com)

## Installation Quick-Start

If you want to replicate this setup, make sure you have the official agent installed globally according to the steps described in the official repo.
Then, you can clone this repository and symlink or copy these files into your local `~/.pi/` directory.

## Structure

```
Pi-dev-config/
├── Context-prompt/
│   └── APPEND_SYSTEM.md
├── Templates/
│   ├── DECISIONS_TEMPLATE.md
│   └── TEST_TEMPLATE.md
└── Skills/
    ├── graphify/
    ├── writing-python/
    ├── refractor-python/
    └── project-backlog-tracker/
```

## Contents

### Context-prompt
| File | Description |
|---|---|
| `APPEND_SYSTEM.md` | Rules appended to the default system prompt: execution boundaries, ambiguity protocol, TODO tracking, output style, data analysis limits. |

### Templates
| File | Description |
|---|---|
| `DECISIONS_TEMPLATE.md` | Required format for project `DECISIONS.md` files. |
| `TEST_TEMPLATE.md` | Required format for isolated option-test logs. |

### Skills
| Skill | Description |
|---|---|
| `graphify` | Converts any input into a knowledge graph with clustered communities and HTML/JSON/Markdown reports. |
| `writing-python` | Coding standards and architecture for Python pipelines, scripts, and CLI tools. |
| `refractor-python` | Post-development cleanup: dead code purge and PEP 8 docstring refactor. |
| `project-backlog-tracker` | Extracts missing features and future improvements into a scannable backlog format. |

## Usage

Skills in `Skills/` mirror the active set registered at `~/.pi/agent/skills/`.
`APPEND_SYSTEM.md` is appended to the agent's base system prompt.

## License

MIT — see [LICENSE](LICENSE).
