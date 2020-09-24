"""Create issue on Github use case."""
from typing import Any
from typing import List
from typing import Union

import github

import git_portfolio.domain.issue as i
import git_portfolio.github_manager as ghm
import git_portfolio.response_objects as res


class GhCreateIssueUseCase:
    """Github create issue use case."""

    def __init__(self, github_manager: ghm.GithubManager) -> None:
        """Initializer."""
        self.github_manager = github_manager

    def execute(
        self, issue: i.Issue, github_repo: str = ""
    ) -> Union[res.ResponseFailure, res.ResponseSuccess]:
        """Create issues."""
        labels = (
            [label.strip() for label in issue.labels.split(",")] if issue.labels else []
        )

        if github_repo:
            output = self._create_issue_from_repo(github_repo, issue, labels)
        else:
            output = ""
            for github_repo in self.github_manager.config.github_selected_repos:
                output += self._create_issue_from_repo(github_repo, issue, labels)
        return res.ResponseSuccess(output)

    def _create_issue_from_repo(
        self, github_repo: str, issue: Any, labels: List[str]
    ) -> str:
        """Create issue from one repository."""
        repo = self.github_manager.github_connection.get_repo(github_repo)
        try:
            repo.create_issue(title=issue.title, body=issue.body, labels=labels)
            return f"{github_repo}: issue created successfully."
        except github.GithubException as github_exception:
            if github_exception.data["message"] == "Issues are disabled for this repo":
                return (
                    f"{github_repo}: {github_exception.data['message']}. "
                    "It may be a fork."
                )

            else:
                return f"{github_repo}: {github_exception.data['message']}."
