from unittest.mock import MagicMock, patch

from src.labeler import apply_labels


@patch("src.labeler.assign_issue")
@patch("src.labeler.ensure_labels_exist")
@patch("src.labeler.load_label_rules")
@patch("src.labeler.load_config")
@patch(
    "src.labeler.translate_to_english",
    side_effect=lambda x: x
)
def test_apply_labels_success(
    mock_translate,
    mock_load_config,
    mock_load_rules,
    mock_ensure_labels,
    mock_assign_issue
):

    mock_load_rules.return_value = {
        "bug": ["error"]
    }

    mock_load_config.return_value = {
        "assignees": {
            "bug": "lead-dev"
        },
        "labeler": {
            "label_colors": {
                "bug": "ff0000"
            }
        }
    }

    issue = MagicMock()
    issue.title = "Critical error"
    issue.body = "Application error on startup"
    issue.number = 1
    issue.labels = []

    repo = MagicMock()

    apply_labels(issue, repo)

    issue.add_to_labels.assert_called_once_with(
        "bug"
    )

    mock_assign_issue.assert_called_once()


@patch("src.labeler.ensure_labels_exist")
@patch("src.labeler.load_label_rules")
@patch(
    "src.labeler.translate_to_english",
    side_effect=lambda x: x
)
def test_apply_labels_no_matches(
    mock_translate,
    mock_load_rules,
    mock_ensure_labels
):

    mock_load_rules.return_value = {
        "bug": ["error"]
    }

    issue = MagicMock()
    issue.title = "New feature"
    issue.body = "Add dark mode"
    issue.number = 2
    issue.labels = []

    repo = MagicMock()

    apply_labels(issue, repo)

    issue.add_to_labels.assert_not_called()


@patch("src.labeler.assign_issue")
@patch("src.labeler.ensure_labels_exist")
@patch("src.labeler.load_label_rules")
@patch("src.labeler.load_config")
@patch(
    "src.labeler.translate_to_english",
    side_effect=lambda x: x
)
def test_apply_labels_skip_existing(
    mock_translate,
    mock_load_config,
    mock_load_rules,
    mock_ensure_labels,
    mock_assign_issue
):

    mock_load_rules.return_value = {
        "bug": ["error"]
    }

    mock_load_config.return_value = {
        "assignees": {
            "bug": "lead-dev"
        },
        "labeler": {
            "label_colors": {
                "bug": "ff0000"
            }
        }
    }

    existing_label = MagicMock()
    existing_label.name = "bug"

    issue = MagicMock()
    issue.title = "Critical error"
    issue.body = "Application error"
    issue.number = 3
    issue.labels = [existing_label]

    repo = MagicMock()

    apply_labels(issue, repo)

    issue.add_to_labels.assert_not_called()

    mock_assign_issue.assert_not_called()