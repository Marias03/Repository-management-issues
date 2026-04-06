import os
from dotenv import load_dotenv
from github import Github

load_dotenv()

token = os.getenv("GITHUB_TOKEN")
repo_name = os.getenv("REPO_NAME")

g = Github(token)
repo = g.get_repo(repo_name)

print(f"Connected to: {repo.full_name}")
print(f"Open issues: {repo.open_issues_count}")
print()

print("TEST 1 - Labeler")
from src.labeler import detect_labels, load_label_rules
rules = load_label_rules()
labels = detect_labels("App crashes on login", "Getting an error when I try to log in", rules)
print(f"   Input: 'App crashes on login'")
print(f"   Detected labels: {labels}")
print()

print("TEST 2 - Duplicate detection (NLP & LLM)")

# --- NLP ---
from src.duplicates.nlpDuplicates import NLPDuplicateDetector

nlp_detector = NLPDuplicateDetector()
text1 = "App crashes on login"
text2 = "Application crashes during login"
nlp_score = nlp_detector.semantic_similarity(text1, text2)
print(f"   [NLP] Similarity score: {round(nlp_score * 100)}%")

# --- LLM ---
from src.duplicates.LLMDuplicates import LLMDuplicateDetector

llm_detector = LLMDuplicateDetector()
llm_result = llm_detector.llm_check(text1, text2)
print(f"   [LLM] Duplicate check result:\n{llm_result.strip() if llm_result else 'No result'}")

print("TEST 3 - Notifier (stale issues)")
from src.notifier import days_since, STALE_DAYS
issues = list(repo.get_issues(state="open"))
if issues:
    for issue in issues[:3]:
        if issue.pull_request:
            continue
        age = days_since(issue.created_at)
        stale = "STALE" if age >= STALE_DAYS and issue.comments == 0 else "ok"
        print(f"   Issue #{issue.number}: {age} days old, {issue.comments} comments -> {stale}")
else:
    print("   No open issues found.")
print()

print("TEST 4 - Closer (commit parsing)")
from src.closer import extract_issue_numbers
messages = [
    "Fix login bug - closes #5",
    "Update readme - fixes #12 and resolves #3",
    "Regular commit without issue reference",
]
for msg in messages:
    numbers = extract_issue_numbers(msg)
    print(f"   '{msg}' -> {numbers if numbers else 'none'}")
print()

print("All tests completed.")