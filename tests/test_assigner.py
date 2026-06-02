from unittest.mock import MagicMock

from src.assigner import assign_issue

def test_assign_issue_success():

    issue = MagicMock()
    issue.number = 1
    issue.assignees = []

    collaborator = MagicMock()
    collaborator.login = "lead-dev"

    repo = MagicMock()
    repo.get_collaborators.return_value = [collaborator]

    config = {
        "assignees": {
            "bug": "lead-dev"
        }
    }

    labels = ["bug"]

    assign_issue(
        issue,
        repo,
        config,
        labels
    )

    issue.add_to_assignees.assert_called_once_with(
        "lead-dev"
    )


def test_assign_issue_not_collaborator():

    issue = MagicMock()
    issue.number = 2
    issue.assignees = []

    collaborator = MagicMock()
    collaborator.login = "another-user"

    repo = MagicMock()
    repo.get_collaborators.return_value = [collaborator]

    config = {
        "assignees": {
            "bug": "lead-dev"
        }
    }

    labels = ["bug"]

    assign_issue(
        issue,
        repo,
        config,
        labels
    )

    issue.add_to_assignees.assert_not_called()


def test_assign_issue_no_matching_label():

    issue = MagicMock()
    issue.number = 3
    issue.assignees = []

    collaborator = MagicMock()
    collaborator.login = "lead-dev"

    repo = MagicMock()
    repo.get_collaborators.return_value = [collaborator]

    config = {
        "assignees": {
            "bug": "lead-dev"
        }
    }

    labels = ["docs"]

    assign_issue(
        issue,
        repo,
        config,
        labels
    )

    issue.add_to_assignees.assert_not_called()


def test_assign_issue_already_assigned():

    existing_assignee = MagicMock()

    issue = MagicMock()
    issue.number = 4
    issue.assignees = [existing_assignee]

    repo = MagicMock()

    config = {
        "assignees": {
            "bug": "lead-dev"
        }
    }

    labels = ["bug"]

    assign_issue(
        issue,
        repo,
        config,
        labels
    )

    issue.add_to_assignees.assert_not_called()