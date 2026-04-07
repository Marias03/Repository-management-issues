

import os
import sys
import json
import logging
from github import Github

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils import setup_logging
from src.labeler import apply_labels
from src.duplicate import handle_duplicates
from src.notifier import check_stale_issues
from src.closer import close_issues_from_push
from src.tone import handle_tone
from src.reporter import generate_report

logger = logging.getLogger(__name__)

 
 
def get_env(key):
    value = os.environ.get(key)
    if not value:
        raise EnvironmentError(f"Environment variable '{key}' is not set.")
    return value


def main():
    setup_logging(level=os.environ.get("LOG_LEVEL", "INFO"))

    # --- Setup ---
    token = get_env("GITHUB_TOKEN")
    repo_name = get_env("REPO_NAME")
    event_name = os.environ.get("GITHUB_EVENT_NAME", "schedule")
    event_path = os.environ.get("GITHUB_EVENT_PATH", "")

    g = Github(token)
    repo = g.get_repo(repo_name)

    logger.info("Event: %s | Repository: %s", event_name, repo_name)

    
    event_data = {}
    if event_path and os.path.exists(event_path):
        with open(event_path, "r", encoding="utf-8") as f:
            event_data = json.load(f)

    if event_name == "issues":
        action = event_data.get("action", "")
        issue_number = event_data.get("issue", {}).get("number")

        if not issue_number:
            logger.warning("No issue number found in event payload.")
            return

        issue = repo.get_issue(issue_number)
        logger.info("Processing issue #%s (action: %s)", issue_number, action)

        if action in ("opened", "edited"):
            logger.info("Applying labels...")
            apply_labels(issue, repo)

            logger.info("Detecting tone...")
            handle_tone(issue, repo)

            if action == "opened":
                logger.info("Checking for duplicates...")
                handle_duplicates(issue, repo)

    elif event_name == "push":
        commits = event_data.get("commits", [])
        if commits:
            logger.info("Processing %d commit(s)...", len(commits))
            close_issues_from_push(repo, commits)
        else:
            logger.info("No commits found in push event.")

    elif event_name == "schedule":
        logger.info("Checking for stale issues...")
        check_stale_issues(repo)

        logger.info("Generating report...")
        generate_report(repo)

    else:
        logger.warning("Event '%s' is not handled.", event_name)

    logger.info("Done.")


if __name__ == "__main__":
    main()
