"""Close issue on Github use case."""
from typing import Union

import git_portfolio.request_objects.issue_list as il
import git_portfolio.responses as res
import git_portfolio.use_cases.gh as gh
import git_portfolio.use_cases.gh_list_issue as li


class GhCloseIssueUseCase(gh.GhUseCase):
    """Github close issue use case."""

    def action(  # type: ignore[override]
        self,
        github_repo: str,
        request_object: Union[il.IssueListValidRequest, il.IssueListInvalidRequest],
    ) -> None:
        """Close issues."""
        github_service_method = "close_issues_from_repo"
        response = li.GhListIssueUseCase(
            self.config_manager, self.github_service
        ).execute(request_object, github_repo)
        if isinstance(response, res.ResponseSuccess):
            self.call_github_service(github_service_method, github_repo, response.value)
        else:
            self.output += f"{github_repo}: no issues match search.\n"
