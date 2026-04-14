# Repository management issues

A Python bot that automates issue management in GitHub repositories using the GitHub Actions CI/CD platform.

## Overview

The bot listens to repository events and reacts automatically — no manual intervention required. It runs entirely in the cloud through GitHub Actions, triggered by issue activity, commits, or a daily schedule.

## Features

**Automatic labeling**
When a new issue is opened, the bot analyzes the title and description to assign relevant labels such as `bug`, `feature`, `docs`, `question`, or `security`. Text is automatically translated to English before analysis, so issues written in any language are supported.

**Duplicate detection**
Supports two methods controlled by the `DUPLICATE_METHOD` environment variable:
- `nlp` — uses sentence-transformers to compare issues semantically. Converts text into numerical vectors and calculates cosine similarity. Issues above 75% similarity receive a `duplicate` label.
- `llm` — uses Gemini AI (gemini-2.5-flash) to determine if two issues describe the same problem. Returns a human-readable explanation of why they are duplicates.

**Tone detection**
Classifies the tone of each issue as `urgent`, `aggressive`, `confused`, or `normal`. Each tone triggers a different automatic comment. Urgent issues also receive the `urgent` label for prioritization.

**Stale notifications**
A daily scheduled job checks all open issues. Any issue with no comments after 7 days receives a reminder comment and the `needs-attention` label.

**Auto closing**
When a commit message contains `closes #N`, `fixes #N`, or `resolves #N`, the bot automatically closes the referenced issue and leaves a comment with a link to the commit.

**Daily report**
Every day at 09:00 UTC, the bot generates a `report.md` file in the repository with a summary of open/closed issues, label distribution, oldest issues, and issues with no response.

## Tech stack

- Python 3.10+
- **PyGithub** — GitHub API client
- **sentence-transformers** — semantic NLP for duplicate detection (nlp method)
- **google-generativeai** — Gemini LLM for advanced duplicate detection (llm method)
- **deep-translator** — multilanguage support
- GitHub Actions — cloud execution and scheduling

## Project structure
## Project structure

```
├── .github/
│   └── workflows/
│       └── bot.yml              # GitHub Actions workflow
├── config/
│   ├── labels.json              # Keyword rules for label detection
│   └── bot_config.json          # Centralized bot configuration
├── src/
│   ├── main.py                  # Entry point — routes events to modules
│   ├── utils.py                 # Shared utilities and helpers
│   ├── labeler.py               # Label detection with translation
│   ├── duplicate.py             # NLP-based duplicate detection
│   ├── tone.py                  # Tone classification and auto comments
│   ├── notifier.py              # Stale issue notifications
│   ├── closer.py                # Auto close from commit messages
│   └── reporter.py              # Daily statistics report
├── test_bot.py                  # Local test script
└── requirements.txt
```

## Technical Details

**Architecture**
The bot follows a modular architecture where each module handles one responsibility. `main.py` acts as the coordinator — it reads the GitHub event and routes it to the correct module.

**Event flow**
- Issue created → `labeler.py` → `tone.py` → `duplicate.py`
- Issue edited → `labeler.py` → `tone.py`
- Push to main → `closer.py`
- Daily schedule → `notifier.py` → `reporter.py`

**Duplicate detection methods**
- `nlp` — the all-MiniLM-L6-v2 model converts text into numerical vectors (embeddings) and calculates cosine similarity. A score above 0.75 triggers a duplicate warning.
- `llm` — sends both issues to Gemini AI with a prompt asking if they describe the same problem. Returns Yes/No with a short explanation.

**Translation**
All text is automatically translated to English before analysis using deep-translator. This ensures consistent keyword matching regardless of the original language.

**Configuration**
All bot constants are centralized in `config/bot_config.json` — similarity threshold, NLP model, label colors, tone keywords and automatic comments. This allows changing values without modifying the source code.

**Logging**
The bot uses Python's logging module configured in `utils.py`. All events are logged with timestamp, level and module name for easy debugging.

## Setup

### 1. Clone and install

```bash
git clone https://github.com/Marias03/Repository-management-issues.git
cd Repository-management-issues
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Environment variables

Create a `.env` file in the project root:
GITHUB_TOKEN=your_personal_access_token
REPO_NAME=your_username/your_repository
LOG_LEVEL=INFO
GEMINI_API_KEY=your_gemini_api_key
DUPLICATE_METHOD=llm

The token needs `repo` and `workflow` scopes.

### 3. Run tests locally

```bash
python test_bot.py
```

## GitHub Actions

The workflow triggers on three event types:

- `issues: opened / edited` — runs labeling, tone detection, and duplicate check
- `push: main` — scans commit messages for `closes #N` patterns
- `schedule: 0 9 * * *` — runs stale check and generates the daily report

No additional secrets are required beyond the default `GITHUB_TOKEN` provided by GitHub Actions.

## Supported languages

The bot uses automatic translation before text analysis, so issues can be written in any language. Tested with English, Spanish, and Russian.
