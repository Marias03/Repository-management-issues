# GitHub Issues Bot

A Python bot that automatically manages issues in a GitHub repository.
Runs in the cloud via GitHub Actions — no server required.

## What it does

| Feature | Description |
|---|---|
| Auto labeling | Detects the issue type and adds labels automatically |
| Duplicate detection | Uses NLP to find semantically similar issues |
| Tone detection | Identifies urgent, aggressive, or confused issues |
| Auto comments | Leaves a comment on every new issue |
| Stale notifications | Notifies about issues with no response for 7+ days |
| Auto closing | Closes issues when a commit contains `closes #N` |
| Daily report | Generates a `report.md` with repository statistics |

## Supported languages

The bot understands issues written in any language.
It automatically translates to English before analyzing.

Tested with: English, Spanish, Russian.

## How it works
```
Someone opens an issue on GitHub
           ↓
GitHub notifies GitHub Actions
           ↓
main.py reads the event type
           ↓
calls the right module
           ↓
labeler / duplicate / tone / notifier / closer act
```

## Project structure
```
github-issues-bot/
├── .github/
│   └── workflows/
│       └── bot.yml          # GitHub Actions configuration
├── src/
│   ├── main.py              # Entry point, routes events
│   ├── labeler.py           # Automatic label detection
│   ├── duplicate.py         # NLP semantic duplicate detection
│   ├── tone.py              # Tone detection and auto comments
│   ├── notifier.py          # Stale issue notifications
│   ├── closer.py            # Auto close by commit message
│   └── reporter.py          # Daily statistics report
├── config/
│   └── labels.json          # Label rules and keywords
├── requirements.txt
└── test_bot.py              # Local test script
```

## Tech stack

| Technology | Purpose |
|---|---|
| Python 3.10+ | Main language |
| PyGithub | GitHub API client |
| sentence-transformers | NLP semantic similarity |
| deep-translator | Multilanguage support |
| GitHub Actions | Cloud execution |

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/Marias03/Repository-management-issues.git
cd Repository-management-issues
```

### 2. Create a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file:
```
GITHUB_TOKEN=your_token_here
REPO_NAME=your_username/your_repo
```

### 4. Run tests locally
```bash
python test_bot.py
```

## GitHub Actions setup

The bot runs automatically in the cloud. No setup needed beyond pushing the code.

It triggers on:
- New or edited issues
- Push to main branch
- Every day at 9:00 UTC (for stale issue checks)

## Label reference

| Label | Triggered by |
|---|---|
| `bug` | crash, error, broken, not working... |
| `feature` | add, improvement, request... |
| `docs` | documentation, readme, guide... |
| `question` | how to, confused, help... |
| `security` | vulnerability, exploit, hack... |
| `urgent` | production down, completely broken... |
| `duplicate` | semantically similar to existing issue |
| `needs-attention` | no response for 7+ days |

## Example

Someone opens an issue:
> *"La app no funciona después de la actualización"*

The bot automatically:
1. Translates to English
2. Adds labels `bug` and `urgent`
3. Checks for duplicate issues
4. Leaves a comment: *"This issue has been marked as urgent and will be prioritized."*

All in under 1 min.
