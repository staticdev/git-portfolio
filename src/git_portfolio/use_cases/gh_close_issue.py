"""Close issue on Github use case."""
from __future__ import annotations

import git_portfolio.request_objects.issue_list as il
import git_portfolio.responses as res
import git_portfolio.use_cases.gh as gh
import git_portfolio.views as views


class GhCloseIssueUseCase(gh.GhUseCase):
    """Github close issue use case."""

    def action(  # type: ignore[override]
        self,
        github_repo: str,
        request_object: il.IssueListValidRequest | il.IssueListInvalidRequest,
    ) -> None:
        """Close issues."""
        github_service_method = "close_issues_from_repo"
        response = views.issues(github_repo, self.github_service, request_object)
        if isinstance(response, res.ResponseSuccess):
            self.call_github_service(github_service_method, github_repo, response.value)
        else:
            self.responses.append(
                res.ResponseFailure(
                    res.ResponseTypes.RESOURCE_ERROR,
                    f"{github_repo}: no issues match search.\n",
                )
            )
