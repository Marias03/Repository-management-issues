"""
nlpDuplicates.py — Detects duplicate issues using NLP semantic similarity.
Understands meaning, not just exact words.
"""

from sentence_transformers import SentenceTransformer, util
from deep_translator import GoogleTranslator
from .base import DuplicateDetector

SIMILARITY_THRESHOLD = 0.75
model = SentenceTransformer("all-MiniLM-L6-v2")

class NLPDuplicateDetector(DuplicateDetector):
    def translate_to_english(self,text):
        """Translates any text to English."""
        try:
            if not text or len(text.strip()) == 0:
                return text
            translated = GoogleTranslator(source="auto", target="en").translate(text)
            return translated or text
        except Exception as e:
            print(f"  [duplicate] Translation failed: {e}")
            return text

    def semantic_similarity(self,text_a, text_b):
        """Translates and returns semantic similarity score (0.0 to 1.0)."""
        text_a = self.translate_to_englis(text_a)
        text_b = self.translate_to_english(text_b)
        embeddings = model.encode([text_a, text_b], convert_to_tensor=True)
        score = util.cos_sim(embeddings[0], embeddings[1]).item()
        return score

    def find_duplicates(self,new_issue, repo):
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
            score = self.semantic_similarity(new_text, existing_text)
            if score >= SIMILARITY_THRESHOLD:
                duplicates.append((existing, round(score * 100)))

        return sorted(duplicates, key=lambda x: x[1], reverse=True)

    def handle_duplicates(self,issue, repo):
        """Main function: finds semantic duplicates and leaves a comment."""
        print(f"  [duplicate] Checking issue #{issue.number} for duplicates...")
        duplicates = self.find_duplicates(issue, repo)

        if not duplicates:
            print(f"  [duplicate] No duplicates found.")
            return

        lines = ["**Possible duplicates found:**\n"]
        for dup_issue, score in duplicates[:3]:
            lines.append(f"- #{dup_issue.number} — {dup_issue.title} (similarity: {score}%)")
        lines.append("\nPlease check if this issue is a duplicate before proceeding.")

        issue.create_comment("\n".join(lines))
        issue.add_to_labels("duplicate")
        print(f"  [duplicate] Issue #{issue.number}: {len(duplicates)} duplicate(s) found.")
        