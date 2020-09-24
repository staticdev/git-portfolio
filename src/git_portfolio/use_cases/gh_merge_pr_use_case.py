"""Merge pull request on Github use case."""
from typing import Any

import github

import git_portfolio.github_manager as ghm
import git_portfolio.use_cases.gh_delete_branch_use_case as dbr
from git_portfolio.domain.pull_request_merge import PullRequestMerge


class GhMergePrUseCase:
    """Github merge pull request use case."""

    def __init__(self, github_manager: ghm.GithubManager) -> None:
        """Initializer."""
        self.github_manager = github_manager

    def execute(self, pr_merge: PullRequestMerge, github_repo: str = "") -> None:
        """Merge pull requests."""
        # Important note: base and head arguments have different import formats.
        # https://developer.github.com/v3/pulls/#list-pull-requests
        # head needs format "user/org:branch"
        head = f"{pr_merge.prefix}:{pr_merge.head}"
        state = "open"

        if github_repo:
            self._merge_pull_request_from_repo(github_repo, head, pr_merge, state)
        else:
            for github_repo in self.github_manager.config.github_selected_repos:
                self._merge_pull_request_from_repo(github_repo, head, pr_merge, state)

    def _merge_pull_request_from_repo(
        self, github_repo: str, head: str, pr_merge: Any, state: str
    ) -> None:
        """Merge pull request from one repository."""
        repo = self.github_manager.github_connection.get_repo(github_repo)
        pulls = repo.get_pulls(state=state, base=pr_merge.base, head=head)
        if pulls.totalCount == 1:
            pull = pulls[0]
            if pull.mergeable:
                try:
                    pull.merge()
                    print(f"{github_repo}: PR merged successfully.")
                    if pr_merge.delete_branch:
                        delete_branch_use_case = dbr.GhDeleteBranchUseCase(
                            self.github_manager
                        )
                        delete_branch_use_case.execute(pr_merge.head, github_repo)
                except github.GithubException as github_exception:
                    print(f"{github_repo}: {github_exception.data['message']}.")
            else:
                print(
                    (
                        f"{github_repo}: PR not mergeable, GitHub checks may be "
                        "running."
                    )
                )
        else:
            print(
                (
                    f"{github_repo}: no open PR found for {pr_merge.base}:"
                    f"{pr_merge.head}."
                )
            )
