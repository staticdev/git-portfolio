"""Create pull request on Github use case."""
from typing import Union

import git_portfolio.domain.pull_request as pr
import git_portfolio.github_manager as ghm
import git_portfolio.response_objects as res


class GhCreatePrUseCase:
    """Github merge pull request use case."""

    def __init__(self, github_manager: ghm.GithubManager) -> None:
        """Initializer."""
        self.github_manager = github_manager

    def execute(
        self, pr: pr.PullRequest, github_repo: str = ""
    ) -> Union[res.ResponseFailure, res.ResponseSuccess]:
        """Create pull requests."""
        if github_repo:
            if pr.link_issues:
                self.github_manager.link_issues(github_repo, pr)
            output = self.github_manager.create_pull_request_from_repo(github_repo, pr)
        else:
            output = ""
            if pr.link_issues:
                for github_repo in self.github_manager.config.github_selected_repos:
                    self.github_manager.link_issues(github_repo, pr)
                    output += self.github_manager.create_pull_request_from_repo(
                        github_repo, pr
                    )
            else:
                for github_repo in self.github_manager.config.github_selected_repos:
                    output += self.github_manager.create_pull_request_from_repo(
                        github_repo, pr
                    )
        return res.ResponseSuccess(output)
