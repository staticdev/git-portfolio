"""Create issue on Github use case."""
from typing import Union

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
        if github_repo:
            output = self.github_manager.create_issue_from_repo(github_repo, issue)
        else:
            output = ""
            for github_repo in self.github_manager.config.github_selected_repos:
                output += self.github_manager.create_issue_from_repo(github_repo, issue)
        return res.ResponseSuccess(output)
