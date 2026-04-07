from unittest.mock import patch
from src.tone import detect_tone


@patch("src.tone.translate_to_english", side_effect=lambda x: x)
def test_detect_urgent(mock_translate):
    tone = detect_tone("URGENT: production is down", "")
    assert tone == "urgent"


@patch("src.tone.translate_to_english", side_effect=lambda x: x)
def test_detect_aggressive(mock_translate):
    tone = detect_tone("This is garbage", "Terrible software")
    assert tone == "aggressive"


@patch("src.tone.translate_to_english", side_effect=lambda x: x)
def test_detect_confused(mock_translate):
    tone = detect_tone("How do I configure this?", "")
    assert tone == "confused"


@patch("src.tone.translate_to_english", side_effect=lambda x: x)
def test_detect_normal(mock_translate):
    tone = detect_tone("Please add dark mode", "")
    assert tone == "normal"


@patch("src.tone.translate_to_english", side_effect=lambda x: x)
def test_detect_urgent_from_body(mock_translate):
    tone = detect_tone("Login issue", "Production is down for all users")
    assert tone == "urgent"


@patch("src.tone.translate_to_english", side_effect=lambda x: x)
def test_detect_aggressive_from_body(mock_translate):
    tone = detect_tone("Login problem", "Terrible and unacceptable behavior")
    assert tone == "aggressive"
