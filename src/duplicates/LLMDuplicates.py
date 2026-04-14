# src/duplicates/LLMDuplicates.py
import os
from google import genai
from .base import DuplicateDetector
from dotenv import load_dotenv
import pathlib

# Загружаем .env
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY is not set in .env or environment variables!")

# создаём клиента
client = genai.Client(api_key=API_KEY)


class LLMDuplicateDetector(DuplicateDetector):
    """
    Detects duplicate GitHub issues using Gemini LLM.
    """

    def llm_check(self, text_a: str, text_b: str) -> str | None:
        """
        Uses Gemini to check if two texts are duplicates.
        """
        prompt = f"""
You are an assistant that detects duplicate GitHub issues.

Issue A:
{text_a}

Issue B:
{text_b}

Are these two issues describing the same problem?

Answer ONLY in this format:
Duplicate: Yes/No
Reason: <short explanation>
"""

        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash", contents=prompt
            )
            # text field contains the generated text
            return response.text
        except Exception as e:
            print(f"[duplicate][LLM] Error: {e}")
            return None

    def find_duplicates(self, new_issue, repo) -> list:
        new_text = new_issue.title + " " + (new_issue.body or "")
        duplicates = []

        for existing in repo.get_issues(state="open"):
            if existing.number == new_issue.number:
                continue

            existing_text = existing.title + " " + (existing.body or "")
            result = self.llm_check(new_text, existing_text)

            # Если вывод содержит "Duplicate: Yes"
            if result and "Duplicate: Yes" in result:
                duplicates.append((existing, result))

        return duplicates

    def handle_duplicates(self, issue, repo) -> None:
        print(f"[duplicate][LLM] Checking issue #{issue.number}...")

        duplicates = self.find_duplicates(issue, repo)

        if not duplicates:
            print("[duplicate][LLM] No duplicates found.")
            return

        lines = ["**Possible duplicates found (LLM):**\n"]
        for dup_issue, explanation in duplicates[:3]:
            lines.append(f"- #{dup_issue.number} — {dup_issue.title}")
            lines.append(f"  {explanation.strip()}")

        lines.append("\nPlease check if this issue is a duplicate.")

        issue.create_comment("\n".join(lines))
        issue.add_to_labels("duplicate")

        print(f"[duplicate][LLM] Found {len(duplicates)} duplicates.")
