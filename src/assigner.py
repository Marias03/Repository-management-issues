from github import GithubException
import logging

logger = logging.getLogger(__name__)

def assign_issue(issue, repo, config, labels):

    if issue.assignees:
        return

    assignee_map = config.get("assignees", {})

    collaborators = {
        user.login
        for user in repo.get_collaborators()
    }

    for label in labels:

        username = assignee_map.get(label)

        if not username:
            continue

        if username not in collaborators:

            logger.warning(
                "%s is not collaborator",
                username
            )

            continue

        try:

            issue.add_to_assignees(username)

            logger.info(
                "Issue #%s assigned to %s",
                issue.number,
                username
            )

            return

        except GithubException as e:

            logger.error(
                "Assignment error: %s",
                str(e)
            )