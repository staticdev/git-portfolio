"""List issue on Github use case."""
from typing import Union

import git_portfolio.request_objects.issue_list as il
import git_portfolio.responses as res
import git_portfolio.use_cases.gh as gh


class GhListIssueUseCase(gh.GhUseCase):
    """Github list issue use case."""

    def execute(
        self,
        request: Union[il.IssueListValidRequest, il.IssueListInvalidRequest],
        github_repo: str,
    ) -> Union[res.ResponseSuccess, res.ResponseFailure]:
        """Return a list of matching issues."""
        if isinstance(request, il.IssueListInvalidRequest):
            return res.build_response_from_invalid_request(request)
        try:
            issues = self.github_service.list_issues_from_repo(github_repo, request)
            return res.ResponseSuccess(issues)
        except Exception as exc:
            return res.ResponseFailure(res.ResponseTypes.SYSTEM_ERROR, exc)
