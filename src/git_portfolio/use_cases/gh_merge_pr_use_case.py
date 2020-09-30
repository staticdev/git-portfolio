"""Merge pull request on Github use case."""
from typing import Union

import git_portfolio.config_manager as cm
import git_portfolio.domain.pull_request_merge as prm
import git_portfolio.github_service as ghs
import git_portfolio.response_objects as res
import git_portfolio.use_cases.gh_delete_branch_use_case as dbr


class GhMergePrUseCase:
    """Github merge pull request use case."""

    def __init__(
        self, config_manager: cm.ConfigManager, github_service: ghs.GithubService
    ) -> None:
        """Initializer."""
        self.config_manager = config_manager
        self.github_service = github_service

    def execute(
        self, pr_merge: prm.PullRequestMerge, github_repo: str = ""
    ) -> Union[res.ResponseFailure, res.ResponseSuccess]:
        """Merge pull requests."""
        if github_repo:
            output = self.github_service.merge_pull_request_from_repo(
                github_repo, pr_merge
            )
            if pr_merge.delete_branch:
                delete_branch_use_case = dbr.GhDeleteBranchUseCase(
                    self.config_manager, self.github_service
                )
                delete_branch_use_case.execute(pr_merge.head, github_repo)
        else:
            output = ""
            if pr_merge.delete_branch:
                for github_repo in self.config_manager.config.github_selected_repos:
                    output += self.github_service.merge_pull_request_from_repo(
                        github_repo, pr_merge
                    )
                    delete_branch_use_case = dbr.GhDeleteBranchUseCase(
                        self.config_manager, self.github_service
                    )
                    delete_branch_use_case.execute(pr_merge.head, github_repo)
            else:
                for github_repo in self.config_manager.config.github_selected_repos:
                    output += self.github_service.merge_pull_request_from_repo(
                        github_repo, pr_merge
                    )
        return res.ResponseSuccess(output)
