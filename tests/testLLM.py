from src.duplicates import LLMDuplicates


class FakeIssue:
    def __init__(self, number, title, body=""):
        self.number = number
        self.title = title
        self.body = body

    def create_comment(self, text):
        print(f"[Comment for #{self.number}]:\n{text}\n")

    def add_to_labels(self, label):
        print(f"[Label added to #{self.number}]: {label}")


new_issue = FakeIssue(
    1, "App crashes on login", "Every time I try to login, the app crashes."
)
existing_issues = [
    FakeIssue(2, "Login failure", "App throws an error during authentication."),
    FakeIssue(3, "UI glitch", "Button layout breaks on small screens."),
]


# создаём детектор
detector = LLMDuplicates.LLMDuplicateDetector()

# проверяем дубликаты через llm_check
for existing in existing_issues:
    result = detector.llm_check(
        new_issue.title + " " + new_issue.body, existing.title + " " + existing.body
    )
    print(f"Issue #{existing.number} check result:\n{result}\n")
