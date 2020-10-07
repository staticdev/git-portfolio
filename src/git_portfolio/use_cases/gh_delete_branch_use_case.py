"""Delete branch on Github use case."""
from typing import Union

import git_portfolio.config_manager as cm
import git_portfolio.github_service as ghs
import git_portfolio.response_objects as res


class GhDeleteBranchUseCase:
    """Github delete branch use case."""

    def __init__(
        self, config_manager: cm.ConfigManager, github_service: ghs.GithubService
    ) -> None:
        """Initializer."""
        self.config_manager = config_manager
        self.github_service = github_service

    def execute(
        self, branch: str, github_repo: str = ""
    ) -> Union[res.ResponseFailure, res.ResponseSuccess]:
        """Delete branches."""
        if github_repo:
            output = self.github_service.delete_branch_from_repo(github_repo, branch)
        else:
            output = ""
            for github_repo in self.config_manager.config.github_selected_repos:
                output += self.github_service.delete_branch_from_repo(
                    github_repo, branch
                )
        return res.ResponseSuccess(output)
