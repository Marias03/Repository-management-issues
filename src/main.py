"""
main.py — Entry point. Reads the GitHub event and calls the right module.
"""

import os
import sys
import json
from github import Github

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.labeler import apply_labels
from src.duplicates.LLMDuplicates import LLMDuplicateDetector
from src.duplicates.nlpDuplicates import NLPDuplicateDetector
from src.notifier import check_stale_issues
from src.closer import close_issues_from_push
from src.tone import handle_tone
from src.reporter import generate_report


def get_env(key):
    value = os.environ.get(key)
    if not value:
        raise EnvironmentError(f"Environment variable '{key}' is not set.")
    return value


def main():
    # --- Setup ---
    token = get_env("GITHUB_TOKEN")
    repo_name = get_env("REPO_NAME")
    event_name = os.environ.get("GITHUB_EVENT_NAME", "schedule")
    event_path = os.environ.get("GITHUB_EVENT_PATH", "")

    g = Github(token)
    repo = g.get_repo(repo_name)

    print(f"[bot] Event: {event_name} | Repository: {repo_name}")

    # --- Read event payload ---
    event_data = {}
    if event_path and os.path.exists(event_path):
        with open(event_path, "r", encoding="utf-8") as f:
            event_data = json.load(f)

    # --- Route by event type ---

    if event_name == "issues":
        action = event_data.get("action", "")
        issue_number = event_data.get("issue", {}).get("number")

        if not issue_number:
            print("[bot] No issue number found in event.")
            return

        issue = repo.get_issue(issue_number)
        print(f"[bot] Processing issue #{issue_number} (action: {action})")

        if action in ("opened", "edited"):
            print("[bot] -> Applying labels...")
            apply_labels(issue, repo)

            print("[bot] -> Detecting tone...")
            handle_tone(issue, repo)

            if action == "opened":
                print("[bot] -> Checking for duplicates...")

                # Выбираем метод через переменную окружения
                method = os.environ.get("DUPLICATE_METHOD", "nlp")  # 'nlp' или 'llm'

                if method.lower() == "llm":
                    detector = LLMDuplicateDetector()
                else:
                    detector = NLPDuplicateDetector()

                detector.handle_duplicates(issue, repo)

    elif event_name == "push":
        commits = event_data.get("commits", [])
        if commits:
            print(f"[bot] -> Processing {len(commits)} commit(s)...")
            close_issues_from_push(repo, commits)
        else:
            print("[bot] No commits found in push event.")

    elif event_name == "schedule":
        print("[bot] -> Checking for stale issues...")
        check_stale_issues(repo)

        print("[bot] -> Generating report...")
        generate_report(repo)

    else:
        print(f"[bot] Event '{event_name}' is not handled.")

    print("[bot] Done.")


if __name__ == "__main__":
    main()