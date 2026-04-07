"""
tone.py — Detects the tone of an issue and leaves an automatic comment.
"""

from src.utils import translate_to_english

TONES = {
    "urgent": [
        "production down", "blocking", "p0", "hotfix",
        "not working", "broken", "stopped working", "cant login",
        "can't login", "cannot login", "critical", "emergency",
        "everything is down", "nothing works", "completely broken",
        "affecting all users", "major issue", "severe", "outage",
        "system down", "service down", "site down", "app down",
        "production is down", "is down", "all users",
        "does not work", "doesn't work", "no longer works",
        "app not working", "not functioning"
    ],
    "aggressive": [
        "terrible", "awful", "horrible", "unacceptable", "ridiculous",
        "useless", "garbage", "stupid", "worst", "hate", "angry",
        "furious", "disgusting", "incompetent"
    ],
    "confused": [
        "not sure", "confused", "don't understand", "unclear",
        "how do i", "how to", "what is", "why is", "i don't know",
        "no idea", "lost", "stuck"
    ],
}

COMMENTS = {
    "urgent": "This issue has been marked as **urgent** and will be prioritized.",
    "aggressive": "Thank you for your feedback. We have flagged this issue for immediate attention.",
    "confused": "Thank you for reaching out. We will review your question and get back to you.",
    "normal": "Thank you for reporting this. Our team will review it and respond as soon as possible.",
}

# Marker used to identify previously posted tone comments
_TONE_MARKER = "<!-- bot:tone-comment -->"


def translate_to_english_tone(text):
    return translate_to_english(text, module="tone")


def detect_tone(title, body):
    """Translates and analyzes the title and body, returns the tone."""
    translated_title = translate_to_english_tone(title)
    translated_body = translate_to_english_tone(body or "")
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
    print(f"  [tone] Issue #{issue.number}: tone detected -> {tone}")

    if tone != "normal":
        label_map = {
            "urgent": "urgent",
            "aggressive": "needs-attention",
            "confused": "needs-clarification",
        }
        color_map = {
            "urgent": "b60205",
            "needs-attention": "e99695",
            "needs-clarification": "fbca04",
        }
        label_name = label_map[tone]
        existing = {label.name for label in repo.get_labels()}
        if label_name not in existing:
            color = color_map.get(label_name, "ededed")
            repo.create_label(name=label_name, color=color)

        current = {label.name for label in issue.labels}
        if label_name not in current:
            issue.add_to_labels(label_name)

    if already_commented_tone(issue):
        print(f"  [tone] Issue #{issue.number}: tone comment already posted, skipping.")
        return

    comment_body = f"{_TONE_MARKER}\n{COMMENTS[tone]}"
    issue.create_comment(comment_body)
    print(f"  [tone] Issue #{issue.number}: comment left for tone '{tone}'.")
