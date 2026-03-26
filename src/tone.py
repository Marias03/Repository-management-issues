"""
tone.py — Detects the tone of an issue based on its text.
"""

TONES = {
    "urgent": [
        "urgent", "asap", "immediately", "critical", "emergency",
        "production down", "blocking", "p0", "hotfix", "right now"
    ],
    "aggressive": [
        "terrible", "awful", "horrible", "unacceptable", "ridiculous",
        "useless", "garbage", "stupid", "worst", "hate", "angry",
        "furious", "disgusting", "incompetent"
    ],
    "confused": [
        "not sure", "confused", "don't understand", "unclear", "help",
        "how do i", "how to", "what is", "why is", "i don't know",
        "no idea", "lost", "stuck"
    ],
}


def detect_tone(title, body):
    """
    Analyzes the title and body of an issue and returns its tone.
    Possible values: urgent, aggressive, confused, normal
    """
    text = (title + " " + (body or "")).lower()

    for tone, keywords in TONES.items():
        if any(kw.lower() in text for kw in keywords):
            return tone

    return "normal"


def handle_tone(issue, repo):
    """Main function: detects tone and applies the corresponding label."""
    tone = detect_tone(issue.title, issue.body or "")

    print(f"  [tone] Issue #{issue.number}: tone detected -> {tone}")

    if tone == "normal":
        return

    label_map = {
        "urgent": "urgent",
        "aggressive": "needs-attention",
        "confused": "needs-clarification",
    }

    color_map = {
        "urgent": "b60205",
        "needs-clarification": "fbca04",
    }

    # Create label if it does not exist
    label_name = label_map[tone]
    existing = {label.name for label in repo.get_labels()}
    if label_name not in existing:
        color = color_map.get(label_name, "ededed")
        repo.create_label(name=label_name, color=color)

    # Apply label
    current = {label.name for label in issue.labels}
    if label_name not in current:
        issue.add_to_labels(label_name)

    # Leave a comment only for urgent or aggressive
    if tone == "urgent":
        issue.create_comment(
            "This issue has been marked as **urgent** and will be prioritized."
        )
    elif tone == "aggressive":
        issue.create_comment(
            "Thank you for your feedback. We have flagged this issue for immediate attention."
        )
        