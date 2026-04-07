

from datetime import datetime, timezone


STALE_DAYS = 7
NOTIFY_LABEL = "needs-attention"


def days_since(dt):
    
    now = datetime.now(timezone.utc)
    delta = now - dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else now - dt
    return delta.days


def already_notified(issue):
  
    marker = "has been waiting for a response for"
    for comment in issue.get_comments():
        if marker in comment.body:
            return True
    return False


def check_stale_issues(repo):
  
    print("  [notifier] Checking for stale issues...")
    notified_count = 0

    for issue in repo.get_issues(state="open"):
        if issue.pull_request:
            continue

        age = days_since(issue.created_at)
        comment_count = issue.comments

        if age >= STALE_DAYS and comment_count == 0:
            if already_notified(issue):
                print(f"    Issue #{issue.number}: already notified, skipping.")
                continue

            message = (
                f"This issue has been waiting for a response for **{age} days** "
                f"with no comments.\n\n"
                f"Please take a look or close it if it is no longer relevant."
            )
            issue.create_comment(message)

            current_labels = {label.name for label in issue.labels}
            if NOTIFY_LABEL not in current_labels:
                issue.add_to_labels(NOTIFY_LABEL)

            print(f"    Issue #{issue.number}: notification sent ({age} days with no response).")
            notified_count += 1

    print(f"  [notifier] Done. Issues notified: {notified_count}.")