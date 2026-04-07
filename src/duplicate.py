"""
duplicate.py — Detects duplicate issues using NLP semantic similarity.
Understands meaning, not just exact words.
"""

import logging
from sentence_transformers import SentenceTransformer, util
from src.utils import translate_to_english, load_config

logger = logging.getLogger(__name__)

_cfg = load_config()["duplicate"]

SIMILARITY_THRESHOLD = _cfg["similarity_threshold"]
_model = SentenceTransformer(_cfg["model"])
_MAX_RESULTS = _cfg["max_results"]


def semantic_similarity(text_a, text_b):
    """Translates and returns semantic similarity score (0.0 to 1.0)."""
    text_a = translate_to_english(text_a)
    text_b = translate_to_english(text_b)
    embeddings = _model.encode([text_a, text_b], convert_to_tensor=True)
    score = util.cos_sim(embeddings[0], embeddings[1]).item()
    return score


def find_duplicates(new_issue, repo):
    """
    Compares a new issue against all open issues using NLP.
    Returns a list of (issue, score) for semantically similar ones.
    """
    new_text = new_issue.title + " " + (new_issue.body or "")
    duplicates = []

    for existing in repo.get_issues(state="open"):
        if existing.number == new_issue.number:
            continue
        existing_text = existing.title + " " + (existing.body or "")
        score = semantic_similarity(new_text, existing_text)
        if score >= SIMILARITY_THRESHOLD:
            duplicates.append((existing, round(score * 100)))

    return sorted(duplicates, key=lambda x: x[1], reverse=True)


def handle_duplicates(issue, repo):
    """Main function: finds semantic duplicates and leaves a comment."""
    logger.debug("Checking issue #%s for duplicates...", issue.number)
    duplicates = find_duplicates(issue, repo)

    if not duplicates:
        logger.debug("Issue #%s: no duplicates found.", issue.number)
        return

    lines = ["**Possible duplicates found:**\n"]
    for dup_issue, score in duplicates[:_MAX_RESULTS]:
        lines.append(f"- #{dup_issue.number} — {dup_issue.title} (similarity: {score}%)")
    lines.append("\nPlease check if this issue is a duplicate before proceeding.")

    issue.create_comment("\n".join(lines))
    issue.add_to_labels("duplicate")
    logger.info("Issue #%s: %d duplicate(s) found.", issue.number, len(duplicates))
