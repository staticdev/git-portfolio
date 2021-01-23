"""Close issue on Github use case."""
from typing import Union

import git_portfolio.request_objects.issue_list as il
import git_portfolio.responses as res
import git_portfolio.use_cases.gh as gh
import git_portfolio.use_cases.gh_list_issue as li


class GhCloseIssueUseCase(gh.GhUseCase):
    """Github close issue use case."""

    def execute(
        self,
        request_object: Union[il.IssueListValidRequest, il.IssueListInvalidRequest],
        github_repo: str = "",
    ) -> Union[res.ResponseFailure, res.ResponseSuccess]:
        """Close issues."""
        output = ""
        if github_repo:
            response = li.GhListIssueUseCase(
                self.config_manager, self.github_service
            ).execute(request_object, github_repo)
            if isinstance(response, res.ResponseSuccess):
                output = self.call_github_service(
                    "close_issues_from_repo", output, github_repo, response.value
                )
            else:
                output = f"{github_repo}: no issues closed.\n"
        else:
            for github_repo in self.config_manager.config.github_selected_repos:
                response = li.GhListIssueUseCase(
                    self.config_manager, self.github_service
                ).execute(request_object, github_repo)
                if isinstance(response, res.ResponseSuccess):
                    output = self.call_github_service(
                        "close_issues_from_repo", output, github_repo, response.value
                    )
                else:
                    output += f"{github_repo}: no issues closed.\n"
        return res.ResponseSuccess(output)
