from unittest.mock import patch
from src.labeler import detect_labels

RULES = {
    "bug": ["crash", "error", "broken", "fails"],
    "feature": ["please add", "dark mode", "feature request"],
    "docs": ["documentation", "readme", "guide"],
    "question": ["how do i", "what is", "can i"],
}


@patch("src.labeler.translate_to_english", side_effect=lambda x: x)
def test_detect_bug_label(mock_translate):
    labels = detect_labels("App crash on login", "500 error shown", RULES)
    assert "bug" in labels


@patch("src.labeler.translate_to_english", side_effect=lambda x: x)
def test_detect_feature_label(mock_translate):
    labels = detect_labels("Please add dark mode", "", RULES)
    assert "feature" in labels


@patch("src.labeler.translate_to_english", side_effect=lambda x: x)
def test_detect_docs_label(mock_translate):
    labels = detect_labels(
        "README is unclear", "documentation should be improved", RULES
    )
    assert "docs" in labels


@patch("src.labeler.translate_to_english", side_effect=lambda x: x)
def test_detect_question_label(mock_translate):
    labels = detect_labels("How do I configure this?", "", RULES)
    assert "question" in labels


@patch("src.labeler.translate_to_english", side_effect=lambda x: x)
def test_detect_multiple_labels(mock_translate):
    labels = detect_labels("README error", "documentation has broken example", RULES)
    assert "docs" in labels
    assert "bug" in labels


@patch("src.labeler.translate_to_english", side_effect=lambda x: x)
def test_detect_no_labels(mock_translate):
    labels = detect_labels("Hello world", "Just saying hi", RULES)
    assert labels == []


@patch("src.labeler.translate_to_english", side_effect=lambda x: x)
def test_detect_from_body_only(mock_translate):
    labels = detect_labels("Setup help", "This guide contains an error", RULES)
    assert "docs" in labels
    assert "bug" in labels
