

import re
import logging

from github import GithubException

logger = logging.getLogger(__name__)

CLOSE_PATTERNS = re.compile(
    r"\b(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)\s+#(\d+)",
    re.IGNORECASE,
)


def extract_issue_numbers(commit_message):
    matches = CLOSE_PATTERNS.findall(commit_message)
    return [int(n) for n in matches]


def find_open_pr_for_issue(repo, issue_number):
    """Returns the first open PR that references the given issue number, or None."""
    keyword = f"#{issue_number}"
    for pr in repo.get_pulls(state="open"):
        body = pr.body or ""
        if keyword in (pr.title + " " + body):
            return pr
    return None


def close_issues_from_push(repo, commits):
    logger.info("Checking commits for 'closes #N'... (%d commit(s) received)", len(commits))
    closed_count = 0
    already_processed = set()

    for commit_data in commits:
        message = commit_data.get("message", "")
        sha = commit_data.get("id", "")[:7]
        author = commit_data.get("author", {}).get("name", "unknown")
        issue_numbers = extract_issue_numbers(message)

        for number in issue_numbers:
            if number in already_processed:
                logger.debug("Issue #%s: already processed in this push, skipping.", number)
                continue

            already_processed.add(number)

            try:
                issue = repo.get_issue(number)

                if issue.state == "closed":
                    logger.debug("Issue #%s: already closed, skipping.", number)
                    continue

                open_pr = find_open_pr_for_issue(repo, number)
                if open_pr:
                    issue.create_comment(
                        f"⚠️ Commit [`{sha}`](https://github.com/{repo.full_name}/commit/{commit_data.get('id', '')}) "
                        f"references this issue, but Pull Request #{open_pr.number} is still open. "
                        f"This issue will not be closed automatically until the PR is merged."
                    )
                    logger.info("Issue #%s: skipped close, open PR #%s found.", number, open_pr.number)
                    continue

                comment = (
                    f"This issue was automatically closed by commit "
                    f"[`{sha}`](https://github.com/{repo.full_name}/commit/{commit_data.get('id', '')}) "
                    f"by **{author}**."
                    f"\n\n> {message}"
                )
                issue.create_comment(comment)
                issue.edit(state="closed")
                logger.info("Issue #%s: closed by commit %s (author: %s).", number, sha, author)
                closed_count += 1

            except GithubException as e:
                if e.status == 404:
                    logger.warning("Issue #%s not found in repo, skipping.", number)
                else:
                    logger.error("Failed to close issue #%s: %s", number, e)

    logger.info("Closer done. Issues closed: %d.", closed_count)
