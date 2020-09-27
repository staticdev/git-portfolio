"""Delete branch on Github use case."""
from typing import Union

import git_portfolio.github_manager as ghm
import git_portfolio.response_objects as res


class GhDeleteBranchUseCase:
    """Github delete branch use case."""

    def __init__(self, github_manager: ghm.GithubManager) -> None:
        """Initializer."""
        self.github_manager = github_manager

    def execute(
        self, branch: str, github_repo: str = ""
    ) -> Union[res.ResponseFailure, res.ResponseSuccess]:
        """Delete branches."""
        if github_repo:
            output = self.github_manager.delete_branch_from_repo(github_repo, branch)
        else:
            output = ""
            for github_repo in self.github_manager.config.github_selected_repos:
                output += self.github_manager.delete_branch_from_repo(
                    github_repo, branch
                )
        return res.ResponseSuccess(output)
