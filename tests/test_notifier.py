from datetime import datetime, timezone
from unittest.mock import Mock

import src.notifier as notifier


def test_already_notified_detects_existing_marker():
    issue = Mock()
    c1 = Mock()
    c1.body = 'This issue has been waiting for a response for **7 days**'
    issue.get_comments.return_value = [c1]

    assert notifier.already_notified(issue) is True


def test_check_stale_issues_notifies_only_stale_without_comments(monkeypatch):
    stale = Mock()
    stale.number = 1
    stale.pull_request = None
    stale.created_at = datetime.now(timezone.utc)
    stale.comments = 0
    stale.labels = []

    fresh = Mock()
    fresh.number = 2
    fresh.pull_request = None
    fresh.created_at = datetime.now(timezone.utc)
    fresh.comments = 0
    fresh.labels = []

    with_comments = Mock()
    with_comments.number = 3
    with_comments.pull_request = None
    with_comments.created_at = datetime.now(timezone.utc)
    with_comments.comments = 2
    with_comments.labels = []

    repo = Mock()
    repo.get_issues.return_value = [stale, fresh, with_comments]

    monkeypatch.setattr(notifier, 'days_since', lambda dt: 10 if dt is stale.created_at else 2)
    monkeypatch.setattr(notifier, 'already_notified', lambda issue: False)

    notifier.check_stale_issues(repo)

    stale.create_comment.assert_called_once()
    stale.add_to_labels.assert_called_once_with(notifier.NOTIFY_LABEL)
    fresh.create_comment.assert_not_called()
    with_comments.create_comment.assert_not_called()
