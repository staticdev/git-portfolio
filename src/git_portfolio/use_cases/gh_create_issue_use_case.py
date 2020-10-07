"""Create issue on Github use case."""
from typing import Union

import git_portfolio.config_manager as cm
import git_portfolio.domain.issue as i
import git_portfolio.github_service as ghs
import git_portfolio.response_objects as res


class GhCreateIssueUseCase:
    """Github create issue use case."""

    def __init__(
        self, config_manager: cm.ConfigManager, github_service: ghs.GithubService
    ) -> None:
        """Initializer."""
        self.config_manager = config_manager
        self.github_service = github_service

    def execute(
        self, issue: i.Issue, github_repo: str = ""
    ) -> Union[res.ResponseFailure, res.ResponseSuccess]:
        """Create issues."""
        if github_repo:
            output = self.github_service.create_issue_from_repo(github_repo, issue)
        else:
            output = ""
            for github_repo in self.config_manager.config.github_selected_repos:
                output += self.github_service.create_issue_from_repo(github_repo, issue)
        return res.ResponseSuccess(output)
