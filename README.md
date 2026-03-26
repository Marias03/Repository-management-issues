# Repository Management Issues Bot

A Python-based GitHub issues bot for basic repository issue management.

This project automates part of the issue workflow by responding to issues and applying labels based on simple rules.

## Features

* Automatic issue labeling
* Automatic issue comments
* GitHub Actions integration
* Modular Python structure for issue management logic

## Current behavior

At the moment, the bot can:

* detect issue conditions based on predefined logic
* add labels such as `bug` and `urgent`
* post an automatic comment on an issue

## Project structure

```text
.
├── .github/
├── config/
├── src/
│   ├── closer.py
│   ├── duplicate.py
│   ├── labeler.py
│   ├── main.py
│   ├── notifier.py
│   ├── reporter.py
│   └── tone.py
├── requirements.txt
└── report.md
```

## Tech stack

* Python
* GitHub Actions

## How it works

1. An issue is created in the repository
2. GitHub Actions runs the bot
3. The bot analyzes the issue
4. The bot applies labels and posts a comment

## Installation

Clone the repository:

```bash
git clone https://github.com/Marias03/Repository-management-issues.git
cd Repository-management-issues
```

Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Purpose

This project was created to practice repository automation and issue handling with Python and GitHub workflows.

## Notes

This repository is still in development, and the bot behavior may continue evolving as new features are added.
