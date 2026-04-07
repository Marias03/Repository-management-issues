from unittest.mock import Mock

from src.closer import extract_issue_numbers, close_issues_from_push


def test_extract_issue_numbers_multiple_patterns():
    msg = 'Fix login; closes #5 and resolves #12, fixed #20'
    assert extract_issue_numbers(msg) == [5, 12, 20]


def test_close_issues_from_push_closes_open_issue():
    issue = Mock()
    issue.state = 'open'
    repo = Mock(full_name='org/repo')
    repo.get_issue.return_value = issue

    commits = [{
        'id': 'abcdef123456',
        'message': 'closes #7',
    }]

    close_issues_from_push(repo, commits)

    issue.create_comment.assert_called_once()
    issue.edit.assert_called_once_with(state='closed')


def test_close_issues_from_push_skips_already_closed_issue():
    issue = Mock()
    issue.state = 'closed'
    repo = Mock(full_name='org/repo')
    repo.get_issue.return_value = issue

    close_issues_from_push(repo, [{'id': 'abc', 'message': 'fixes #9'}])

    issue.create_comment.assert_not_called()
    issue.edit.assert_not_called()
