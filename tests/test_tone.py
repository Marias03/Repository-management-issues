from unittest.mock import Mock

import src.tone as tone


def test_detect_tone_urgent(monkeypatch):
    monkeypatch.setattr(tone, 'translate_to_english', lambda text: text)
    assert tone.detect_tone('URGENT: production down', '') == 'urgent'


def test_already_commented_tone_true_when_marker_present():
    issue = Mock()
    comment = Mock()
    comment.body = '<!-- bot:tone-comment -->\ntext'
    issue.get_comments.return_value = [comment]

    assert tone.already_commented_tone(issue) is True


def test_handle_tone_skips_duplicate_comment(monkeypatch):
    issue = Mock()
    issue.number = 22
    issue.title = 'production down'
    issue.body = ''
    issue.labels = []

    repo = Mock()
    repo.get_labels.return_value = []

    monkeypatch.setattr(tone, 'translate_to_english', lambda text: text)
    monkeypatch.setattr(tone, 'already_commented_tone', lambda issue_obj: True)

    tone.handle_tone(issue, repo)

    issue.create_comment.assert_not_called()


def test_handle_tone_adds_label_and_comment(monkeypatch):
    issue = Mock()
    issue.number = 23
    issue.title = 'production down'
    issue.body = ''
    issue.labels = []

    repo = Mock()
    repo.get_labels.return_value = []

    monkeypatch.setattr(tone, 'translate_to_english', lambda text: text)
    monkeypatch.setattr(tone, 'already_commented_tone', lambda issue_obj: False)

    tone.handle_tone(issue, repo)

    issue.add_to_labels.assert_called_once_with('urgent')
    issue.create_comment.assert_called_once()
