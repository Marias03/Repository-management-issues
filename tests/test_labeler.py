from unittest.mock import Mock

import src.labeler as labeler


def test_detect_labels_matches_expected_keywords(monkeypatch):
    monkeypatch.setattr(labeler, 'translate_to_english', lambda text: text)
    rules = {
        'bug': ['crash', 'error'],
        'feature': ['please add'],
    }

    labels = labeler.detect_labels('App crash on login', 'I get an error', rules)

    assert labels == ['bug']


def test_apply_labels_adds_only_new_labels(monkeypatch):
    issue = Mock()
    issue.number = 10
    issue.title = 'App crash on login'
    issue.body = 'error happens'
    issue.labels = [Mock(name='bug_label')]
    issue.labels[0].name = 'bug'

    repo = Mock()

    monkeypatch.setattr(labeler, 'load_label_rules', lambda config_path=None: {'bug': ['crash'], 'feature': ['add']})
    monkeypatch.setattr(labeler, 'ensure_labels_exist', lambda repo_obj, rules: None)
    monkeypatch.setattr(labeler, 'translate_to_english', lambda text: text)

    labeler.apply_labels(issue, repo)

    issue.add_to_labels.assert_not_called()


def test_apply_labels_adds_detected_missing_labels(monkeypatch):
    issue = Mock()
    issue.number = 11
    issue.title = 'Please add export'
    issue.body = ''
    issue.labels = []

    repo = Mock()

    monkeypatch.setattr(labeler, 'load_label_rules', lambda config_path=None: {'feature': ['please add']})
    monkeypatch.setattr(labeler, 'ensure_labels_exist', lambda repo_obj, rules: None)
    monkeypatch.setattr(labeler, 'translate_to_english', lambda text: text)

    labeler.apply_labels(issue, repo)

    issue.add_to_labels.assert_called_once_with('feature')
