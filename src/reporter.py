"""
reporter.py — Generates a daily markdown report of the repository issues.
"""

from datetime import datetime, timezone
from src.utils import days_since


def generate_report(repo):
    """Main function: generates a report.md file with issue statistics."""
    print("  [reporter] Generating report...")

    all_issues = [i for i in repo.get_issues(state="open") if not i.pull_request]
    closed_issues = [i for i in repo.get_issues(state="closed") if not i.pull_request]

    # --- Statistics ---
    total_open = len(all_issues)
    total_closed = len(closed_issues)
    no_response = [i for i in all_issues if i.comments == 0 and days_since(i.created_at) >= 7]
    duplicates = [i for i in all_issues if any(l.name == "duplicate" for l in i.labels)]
    urgent = [i for i in all_issues if any(l.name == "urgent" for l in i.labels)]

    # --- Labels breakdown ---
    label_count = {}
    for issue in all_issues:
        for label in issue.labels:
            label_count[label.name] = label_count.get(label.name, 0) + 1

    # --- Oldest issues ---
    oldest = sorted(all_issues, key=lambda i: i.created_at)[:5]

    # --- Build report ---
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = []

    lines.append(f"# Issues Report — {repo.full_name}")
    lines.append(f"Generated: {now}")
    lines.append("")

    lines.append("## Summary")
    lines.append(f"- Open issues: {total_open}")
    lines.append(f"- Closed issues: {total_closed}")
    lines.append(f"- No response for 7+ days: {len(no_response)}")
    lines.append(f"- Duplicates: {len(duplicates)}")
    lines.append(f"- Urgent: {len(urgent)}")
    lines.append("")

    lines.append("## Labels breakdown")
    if label_count:
        for label, count in sorted(label_count.items(), key=lambda x: x[1], reverse=True):
            lines.append(f"- {label}: {count}")
    else:
        lines.append("- No labels assigned yet.")
    lines.append("")

    lines.append("## Oldest open issues")
    if oldest:
        for issue in oldest:
            age = days_since(issue.created_at)
            lines.append(f"- #{issue.number} ({age} days) — {issue.title}")
    else:
        lines.append("- No open issues.")
    lines.append("")

    lines.append("## Issues with no response")
    if no_response:
        for issue in no_response:
            age = days_since(issue.created_at)
            lines.append(f"- #{issue.number} ({age} days) — {issue.title}")
    else:
        lines.append("- None.")
    lines.append("")

    # --- Save file ---
    report_content = "\n".join(lines)
    with open("report.md", "w", encoding="utf-8") as f:
        f.write(report_content)

    print(f"  [reporter] Report saved to report.md")
    print(f"  [reporter] Open: {total_open} | Closed: {total_closed} | Stale: {len(no_response)}")
