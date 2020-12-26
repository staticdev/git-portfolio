"""Close issue on Github use case."""
from typing import Union

import git_portfolio.config_manager as cm
import git_portfolio.github_service as ghs
import git_portfolio.request_objects.issue_list as il
import git_portfolio.responses as res
import git_portfolio.use_cases.gh_list_issue as li


class GhCloseIssueUseCase:
    """Github close issue use case."""

    def __init__(
        self, config_manager: cm.ConfigManager, github_service: ghs.GithubService
    ) -> None:
        """Initializer."""
        self.config_manager = config_manager
        self.github_service = github_service

    def execute(
        self,
        request_object: Union[il.IssueListValidRequest, il.IssueListInvalidRequest],
        github_repo: str = "",
    ) -> Union[res.ResponseFailure, res.ResponseSuccess]:
        """Close issues."""
        if github_repo:
            response = li.GhListIssueUseCase(
                self.config_manager, self.github_service
            ).execute(request_object, github_repo)
            if isinstance(response, res.ResponseSuccess):
                output = self.github_service.close_issues_from_repo(
                    github_repo, response.value
                )
            else:
                output = f"{github_repo}: no issues closed.\n"
        else:
            output = ""
            for github_repo in self.config_manager.config.github_selected_repos:
                response = li.GhListIssueUseCase(
                    self.config_manager, self.github_service
                ).execute(request_object, github_repo)
                if isinstance(response, res.ResponseSuccess):
                    output += self.github_service.close_issues_from_repo(
                        github_repo, response.value
                    )
                else:
                    output += f"{github_repo}: no issues closed.\n"
        return res.ResponseSuccess(output)
