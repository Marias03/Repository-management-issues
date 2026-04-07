"""
notifier.py - Notifies about issues that have had no response for too long.
"""

import logging
from src.utils import (
    days_since,
    load_config,
    has_comment_marker,
    build_marked_comment,
)

logger = logging.getLogger(__name__)

_cfg = load_config()["notifier"]
_idem = load_config()["idempotency"]

STALE_DAYS = _cfg["stale_days"]
NOTIFY_LABEL = _cfg["notify_label"]
_STALE_MARKER = _idem["stale_comment_marker"]


def already_notified(issue):
    """Checks if a stale notification was already sent for this issue."""
    return has_comment_marker(issue, _STALE_MARKER)


def check_stale_issues(repo):
    """Main function: checks all open issues and notifies about stale ones."""
    logger.info("Checking for stale issues (threshold: %d days)...", STALE_DAYS)
    notified_count = 0

    for issue in repo.get_issues(state="open"):
        if issue.pull_request:
            continue

        age = days_since(issue.created_at)
        comment_count = issue.comments

        if age >= STALE_DAYS and comment_count == 0:
            if already_notified(issue):
                logger.debug("Issue #%s: already notified, skipping.", issue.number)
                continue

            body = (
                f"This issue has been waiting for a response for **{age} days** "
                f"with no comments.\n\n"
                f"Please take a look or close it if it is no longer relevant."
            )
            issue.create_comment(build_marked_comment(_STALE_MARKER, body))

            current_labels = {label.name for label in issue.labels}
            if NOTIFY_LABEL not in current_labels:
                issue.add_to_labels(NOTIFY_LABEL)

            logger.info("Issue #%s: stale notification sent (%d days, 0 comments).", issue.number, age)
            notified_count += 1

    logger.info("Stale check done. Issues notified: %d.", notified_count)
