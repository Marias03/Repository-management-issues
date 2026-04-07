"""
utils.py — Shared utility functions used across bot modules.
"""

import os
import json
import logging
from datetime import datetime, timezone
from deep_translator import GoogleTranslator

_config_cache = None

logger = logging.getLogger(__name__)


def setup_logging(level: str = "INFO") -> None:
    """
    Configures the root logger for the entire bot.
    Should be called once from main.py at startup.

    Format: 2026-04-07 12:00:00 | INFO     | src.labeler | Labels added -> ['bug']
    """
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    handler = logging.StreamHandler()
    handler.setLevel(numeric_level)
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(numeric_level)
    # Avoid adding duplicate handlers if setup_logging is called more than once
    if not root.handlers:
        root.addHandler(handler)


def load_config(config_path=None):
    """
    Loads bot_config.json and caches it for the lifetime of the process.
    Returns the full config dict.
    """
    global _config_cache
    if _config_cache is not None:
        return _config_cache
    if config_path is None:
        config_path = get_config_path("config/bot_config.json")
    with open(config_path, "r", encoding="utf-8") as f:
        _config_cache = json.load(f)
    return _config_cache


def translate_to_english(text: str) -> str:
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
        logger.warning("Translation failed, using original text: %s", e)
        return text


def days_since(dt) -> int:
    """Returns the number of full days elapsed since the given datetime."""
    now = datetime.now(timezone.utc)
    delta = now - (dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt)
    return delta.days


def get_config_path(relative_path: str) -> str:
    """
    Resolves a config file path relative to the project root,
    regardless of the current working directory.
    Project root is two levels up from this file (src/utils.py -> root).
    """
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(project_root, relative_path)
