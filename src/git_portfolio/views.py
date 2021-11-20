"""List issue on Github use case."""
from typing import Union

import git_portfolio.github_service as ghs
import git_portfolio.request_objects.issue_list as il
import git_portfolio.responses as res


def issues(
    github_repo: str,
    github_service: ghs.GithubService,
    request: Union[il.IssueListValidRequest, il.IssueListInvalidRequest],
) -> Union[res.ResponseSuccess, res.ResponseFailure]:
    """Return a list of matching issues."""
    if isinstance(request, il.IssueListInvalidRequest):
        return res.build_response_from_invalid_request(request)
    try:
        issues = github_service.list_issues_from_repo(github_repo, request)
    except Exception as exc:
        return res.ResponseFailure(res.ResponseTypes.SYSTEM_ERROR, exc)
    return res.ResponseSuccess(issues)
