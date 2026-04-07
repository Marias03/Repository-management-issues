"""
utils.py — Shared utility functions used across bot modules.
"""

import os
from datetime import datetime, timezone
from deep_translator import GoogleTranslator


def translate_to_english(text, module="utils"):
    """
    Translates any text to English using Google Translate.
    Returns the original text if translation fails or text is empty.
    """
    try:
        if not text or len(text.strip()) == 0:
            return text
        translated = GoogleTranslator(source="auto", target="en").translate(text)
        return translated or text
    except Exception as e:
        print(f"  [{module}] Translation failed, using original text: {e}")
        return text


def days_since(dt):
    """Returns the number of full days elapsed since the given datetime."""
    now = datetime.now(timezone.utc)
    delta = now - (dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt)
    return delta.days


def get_config_path(relative_path):
    """
    Resolves a config file path relative to the project root,
    regardless of the current working directory.
    Project root is two levels up from this file (src/utils.py -> root).
    """
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(project_root, relative_path)
