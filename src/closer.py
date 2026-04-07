

import re


CLOSE_PATTERNS = re.compile(
    r"\b(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)\s+#(\d+)",
    re.IGNORECASE,
)


def extract_issue_numbers(commit_message):
    
    matches = CLOSE_PATTERNS.findall(commit_message)
    return [int(n) for n in matches]


def close_issues_from_push(repo, commits):
 
    print("  [closer] Checking commits for 'closes #N'...")
    closed_count = 0

    for commit_data in commits:
        message = commit_data.get("message", "")
        sha = commit_data.get("id", "")[:7]
        issue_numbers = extract_issue_numbers(message)

        for number in issue_numbers:
            try:
                issue = repo.get_issue(number)

                if issue.state == "closed":
                    print(f"    Issue #{number}: already closed, skipping.")
                    continue

                comment = (
                    f"This issue was automatically closed by commit "
                    f"[`{sha}`](https://github.com/{repo.full_name}/commit/{commit_data.get('id', '')})"
                    f".\n\n> {message}"
                )
                issue.create_comment(comment)
                issue.edit(state="closed")
                print(f"    Issue #{number}: closed by commit {sha}.")
                closed_count += 1

            except Exception as e:
                print(f"    Error closing issue #{number}: {e}")

    print(f"  [closer] Done. Issues closed: {closed_count}.")