"""List issue on Github use case."""
from __future__ import annotations

import git_portfolio.github_service as gs
import git_portfolio.request_objects.issue_list as il
import git_portfolio.responses as res


def issues(
    github_repo: str,
    github_service: gs.AbstractGithubService,
    request: il.IssueListValidRequest | il.IssueListInvalidRequest,
) -> res.Response:
    """Return a list of matching issues."""
    if isinstance(request, il.IssueListInvalidRequest):
        return res.build_response_from_invalid_request(request)
    try:
        issues = github_service.list_issues_from_repo(github_repo, request)
    except Exception as exc:
        return res.ResponseFailure(res.ResponseTypes.SYSTEM_ERROR, exc)
    return res.ResponseSuccess(issues)
