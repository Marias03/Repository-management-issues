"""
labeler.py — Automatically labels issues based on keywords.
"""

import json


def load_label_rules(config_path="config/labels.json"):
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def detect_labels(title, body, rules):
    """Returns a list of labels that match the issue text."""
    text = (title + " " + (body or "")).lower()
    matched = []
    for label, keywords in rules.items():
        if any(kw.lower() in text for kw in keywords):
            matched.append(label)
    return matched


def ensure_labels_exist(repo, rules):
    """Creates labels in the repo if they don't exist yet."""
    existing = {label.name for label in repo.get_labels()}
    colors = {
        "bug": "d73a4a",
        "feature": "a2eeef",
        "docs": "0075ca",
        "question": "d876e3",
        "security": "e4e669",
        "duplicate": "cfd3d7",
        "needs-attention": "e99695",
    }
    for label_name in list(rules.keys()) + ["duplicate", "needs-attention"]:
        if label_name not in existing:
            color = colors.get(label_name, "ededed")
            repo.create_label(name=label_name, color=color)
            print(f"  [labeler] Label created: {label_name}")


def apply_labels(issue, repo, config_path="config/labels.json"):
    """Main function: detects and applies labels to the issue."""
    rules = load_label_rules(config_path)
    ensure_labels_exist(repo, rules)

    matched = detect_labels(issue.title, issue.body or "", rules)

    if not matched:
        print(f"  [labeler] Issue #{issue.number}: no matching labels found.")
        return

    current_labels = {label.name for label in issue.labels}
    new_labels = [l for l in matched if l not in current_labels]

    if new_labels:
        issue.add_to_labels(*new_labels)
        print(f"  [labeler] Issue #{issue.number}: labels added → {new_labels}")
    else:
        print(f"  [labeler] Issue #{issue.number}: labels already applied.")