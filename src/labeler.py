
import json
import logging
from src.utils import translate_to_english, get_config_path, load_config

logger = logging.getLogger(__name__)


def load_label_rules(config_path=None):
    if config_path is None:
        config_path = get_config_path("config/labels.json")
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def detect_labels(title, body, rules):
    """Translates title and body to English, then matches keywords."""
    translated_title = translate_to_english(title)
    translated_body = translate_to_english(body or "")

    logger.debug("Original title  : %s", title)
    logger.debug("Translated title: %s", translated_title)

    text = (translated_title + " " + translated_body).lower()
    matched = []
    for label, keywords in rules.items():
        if any(kw.lower() in text for kw in keywords):
            matched.append(label)
    return matched


def ensure_labels_exist(repo, rules):
    """Creates labels in the repo if they don't exist yet."""
    existing = {label.name for label in repo.get_labels()}
    colors = load_config()["labeler"]["label_colors"]
    for label_name in list(rules.keys()) + ["duplicate", "needs-attention"]:
        if label_name not in existing:
            color = colors.get(label_name, "ededed")
            repo.create_label(name=label_name, color=color)
            logger.info("Label created: %s", label_name)


def apply_labels(issue, repo, config_path=None):
    """Main function: detects and applies labels to the issue."""
    rules = load_label_rules(config_path)
    ensure_labels_exist(repo, rules)

    matched = detect_labels(issue.title, issue.body or "", rules)

    if not matched:
        logger.info("Issue #%s: no matching labels found.", issue.number)
        return

    current_labels = {label.name for label in issue.labels}
    new_labels = [l for l in matched if l not in current_labels]

    if new_labels:
        issue.add_to_labels(*new_labels)
        logger.info("Issue #%s: labels added -> %s", issue.number, new_labels)
    else:
        logger.debug("Issue #%s: all detected labels already applied.", issue.number)
