
from deep_translator import GoogleTranslator

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


def translate_to_english(text):

    try:
        if not text or len(text.strip()) == 0:
            return text
        translated = GoogleTranslator(source="auto", target="en").translate(text)
        return translated or text
    except Exception as e:
        print(f"  [tone] Translation failed: {e}")
        return text


def detect_tone(title, body):
  
    translated_title = translate_to_english(title)
    translated_body = translate_to_english(body or "")
    text = (translated_title + " " + translated_body).lower()
    for tone, keywords in TONES.items():
        if any(kw.lower() in text for kw in keywords):
            return tone
    return "normal"


def handle_tone(issue, repo):
  
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

    comment = COMMENTS[tone]
    issue.create_comment(comment)
    print(f"  [tone] Issue #{issue.number}: comment left for tone '{tone}'.")