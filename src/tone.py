"""
tone.py — Detects the tone of an issue and leaves an automatic comment.
"""

import logging
from src.utils import translate_to_english, load_config

logger = logging.getLogger(__name__)

_cfg = load_config()["tone"]

TONES = _cfg["tones"]
COMMENTS = _cfg["comments"]

# Marker used to identify previously posted tone comments
_TONE_MARKER = "<!-- bot:tone-comment -->"


def detect_tone(title, body):
    """Translates and analyzes the title and body, returns the tone."""
    translated_title = translate_to_english(title)
    translated_body = translate_to_english(body or "")
    text = (translated_title + " " + translated_body).lower()
    for tone, keywords in TONES.items():
        if any(kw.lower() in text for kw in keywords):
            return tone
    return "normal"


def already_commented_tone(issue):
    """
    Returns True if the bot has already posted a tone comment on this issue.
    Prevents duplicate comments on repeated 'edited' events.
    """
    for comment in issue.get_comments():
        if _TONE_MARKER in comment.body:
            return True
    return False


def handle_tone(issue, repo):
    """Main function: detects tone, applies label if needed, and leaves a comment."""
    tone = detect_tone(issue.title, issue.body or "")
    logger.info("Issue #%s: tone detected -> %s", issue.number, tone)

    if tone != "normal":
        label_map = {
            "urgent": "urgent",
            "aggressive": "needs-attention",
            "confused": "needs-clarification",
        }
        colors = load_config()["labeler"]["label_colors"]
        label_name = label_map[tone]
        existing = {label.name for label in repo.get_labels()}
        if label_name not in existing:
            color = colors.get(label_name, "ededed")
            repo.create_label(name=label_name, color=color)

        current = {label.name for label in issue.labels}
        if label_name not in current:
            issue.add_to_labels(label_name)

    if already_commented_tone(issue):
        logger.debug("Issue #%s: tone comment already posted, skipping.", issue.number)
        return

    comment_body = f"{_TONE_MARKER}\n{COMMENTS[tone]}"
    issue.create_comment(comment_body)
    logger.info("Issue #%s: tone comment posted (tone: %s).", issue.number, tone)
