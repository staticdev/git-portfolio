"""Merge pull request on Github use case."""
from typing import Union

import git_portfolio.domain.pull_request_merge as prm
import git_portfolio.responses as res
import git_portfolio.use_cases.gh as gh
import git_portfolio.use_cases.gh_delete_branch as dbr


class GhMergePrUseCase(gh.GhUseCase):
    """Github merge pull request use case."""

    def execute(
        self, pr_merge: prm.PullRequestMerge, github_repo: str = ""
    ) -> Union[res.ResponseFailure, res.ResponseSuccess]:
        """Merge pull requests."""
        output = ""
        if github_repo:
            output = self.call_github_service(
                "merge_pull_request_from_repo", output, github_repo, pr_merge
            )
            if pr_merge.delete_branch:
                delete_branch_use_case = dbr.GhDeleteBranchUseCase(
                    self.config_manager, self.github_service
                )
                delete_branch_use_case.execute(pr_merge.head, github_repo)
        else:
            if pr_merge.delete_branch:
                for github_repo in self.config_manager.config.github_selected_repos:
                    output = self.call_github_service(
                        "merge_pull_request_from_repo", output, github_repo, pr_merge
                    )
                    delete_branch_use_case = dbr.GhDeleteBranchUseCase(
                        self.config_manager, self.github_service
                    )
                    delete_branch_use_case.execute(pr_merge.head, github_repo)
            else:
                for github_repo in self.config_manager.config.github_selected_repos:
                    output = self.call_github_service(
                        "merge_pull_request_from_repo", output, github_repo, pr_merge
                    )
        return self.generate_response(output)
