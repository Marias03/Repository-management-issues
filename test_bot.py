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

print("TEST 1 - Labeler (no translation needed)")
from src.labeler import load_label_rules
rules = load_label_rules()
from src.labeler import load_label_rules
rules = load_label_rules()
text = "app crashes on login getting an error".lower()
matched = [l for l, kws in rules.items() if any(k in text for k in kws)]
print(f"   Input: App crashes on login")
print(f"   Detected labels: {matched}")
print()

# ------------------------
# TEST 2 - Duplicate detection (NLP + LLM)
# ------------------------
print("TEST 2 - Duplicate detection (NLP + LLM)")

# --- NLP ---
from src.duplicates.nlpDuplicates import NLPDuplicateDetector
nlp_detector = NLPDuplicateDetector()

pairs = [
    ("App crashes on login", "Application fails during login"),
    ("La app no funciona", "The app is not working"),
    ("Please add dark mode", "App crashes on login"),
]

for a, b in pairs:
    nlp_score = nlp_detector.semantic_similarity(a, b)
    result = "DUPLICATE" if nlp_score >= 0.75 else "different"
    print(f"   [NLP] {round(nlp_score*100)}% -> {result} | {a} vs {b}")

# --- LLM ---
from src.duplicates.LLMDuplicates import LLMDuplicateDetector
llm_detector = LLMDuplicateDetector()

for a, b in pairs:
    llm_result = llm_detector.llm_check(a, b)
    print(f"   [LLM] {a} vs {b} -> {llm_result.strip() if llm_result else 'No result'}")

print()

print("TEST 3 - Tone detection")
from src.tone import detect_tone
cases = [
    ("App is completely broken", ""),
    ("This is garbage software", ""),
    ("Please add dark mode", ""),
]
for title, body in cases:
    tone = detect_tone(title, body)
    print(f"   {title!r} -> {tone}")
print()

print("TEST 4 - Notifier")
from src.notifier import days_since, STALE_DAYS
issues = list(repo.get_issues(state="open"))
if issues:
    for issue in issues[:3]:
        if issue.pull_request:
            continue
        age = days_since(issue.created_at)
        stale = "STALE" if age >= STALE_DAYS and issue.comments == 0 else "ok"
        print(f"   Issue #{issue.number}: {age} days old, {issue.comments} comments - {stale}")
else:
    print("   No open issues found.")
print()

print("TEST 5 - Closer")
from src.closer import extract_issue_numbers
messages = [
    "Fix login bug - closes #5",
    "Update readme - fixes #12 and resolves #3",
    "Regular commit without issue reference",
]
for msg in messages:
    numbers = extract_issue_numbers(msg)
    print(f"   {msg} -> {numbers if numbers else 'none'}")
print()

print("TEST 6 - Reporter")
from src.reporter import generate_report
generate_report(repo)
print("   Check report.md file in your project folder")
print()

print("All tests completed.")
