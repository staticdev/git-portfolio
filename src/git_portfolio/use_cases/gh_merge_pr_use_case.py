"""Merge pull request on Github use case."""
from typing import Any
from typing import Union

import github

import git_portfolio.domain.pull_request_merge as prm
import git_portfolio.github_manager as ghm
import git_portfolio.response_objects as res
import git_portfolio.use_cases.gh_delete_branch_use_case as dbr


class GhMergePrUseCase:
    """Github merge pull request use case."""

    def __init__(self, github_manager: ghm.GithubManager) -> None:
        """Initializer."""
        self.github_manager = github_manager

    def execute(
        self, pr_merge: prm.PullRequestMerge, github_repo: str = ""
    ) -> Union[res.ResponseFailure, res.ResponseSuccess]:
        """Merge pull requests."""
        # Important note: base and head arguments have different import formats.
        # https://developer.github.com/v3/pulls/#list-pull-requests
        # head needs format "user/org:branch"
        head = f"{pr_merge.prefix}:{pr_merge.head}"
        state = "open"

        if github_repo:
            output = self._merge_pull_request_from_repo(
                github_repo, head, pr_merge, state
            )
        else:
            output = ""
            for github_repo in self.github_manager.config.github_selected_repos:
                output += self._merge_pull_request_from_repo(
                    github_repo, head, pr_merge, state
                )
        return res.ResponseSuccess(output)

    def _merge_pull_request_from_repo(
        self, github_repo: str, head: str, pr_merge: Any, state: str
    ) -> str:
        """Merge pull request from one repository."""
        repo = self.github_manager.github_connection.get_repo(github_repo)
        pulls = repo.get_pulls(state=state, base=pr_merge.base, head=head)
        if pulls.totalCount == 1:
            pull = pulls[0]
            if pull.mergeable:
                output = ""
                try:
                    pull.merge()
                    output += f"{github_repo}: PR merged successfully.\n"
                    if pr_merge.delete_branch:
                        delete_branch_use_case = dbr.GhDeleteBranchUseCase(
                            self.github_manager
                        )
                        delete_branch_use_case.execute(pr_merge.head, github_repo)
                except github.GithubException as github_exception:
                    output += f"{github_repo}: {github_exception.data['message']}."
                return output
            else:
                return f"{github_repo}: PR not mergeable, GitHub checks may be running."
        else:
            return (
                f"{github_repo}: no open PR found for {pr_merge.base}:"
                f"{pr_merge.head}."
            )
