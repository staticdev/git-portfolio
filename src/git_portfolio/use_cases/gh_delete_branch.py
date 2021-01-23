"""Delete branch on Github use case."""
from typing import Union

import git_portfolio.responses as res
import git_portfolio.use_cases.gh as gh


class GhDeleteBranchUseCase(gh.GhUseCase):
    """Github delete branch use case."""

    def execute(
        self, branch: str, github_repo: str = ""
    ) -> Union[res.ResponseFailure, res.ResponseSuccess]:
        """Delete branches."""
        output = ""
        if github_repo:
            output = self.call_github_service(
                "delete_branch_from_repo", output, github_repo, branch
            )
        else:
            for github_repo in self.config_manager.config.github_selected_repos:
                output = self.call_github_service(
                    "delete_branch_from_repo", output, github_repo, branch
                )
        return self.generate_response(output)
