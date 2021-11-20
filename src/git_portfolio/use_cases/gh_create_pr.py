"""Create pull request on Github use case."""
from typing import Union

import git_portfolio.domain.pull_request as pr
import git_portfolio.request_objects.issue_list as il
import git_portfolio.responses as res
import git_portfolio.use_cases.gh as gh
import git_portfolio.views as views


class GhCreatePrUseCase(gh.GhUseCase):
    """Github merge pull request use case."""

    def action(  # type: ignore[override]
        self,
        github_repo: str,
        pr_obj: pr.PullRequest,
        request_object: Union[il.IssueListValidRequest, il.IssueListInvalidRequest],
    ) -> None:
        """Create pull requests."""
        github_service_method = "create_pull_request_from_repo"
        if pr_obj.link_issues:
            response = views.issues(github_repo, self.github_service, request_object)
            if isinstance(response, res.ResponseSuccess):
                custom_pr = self.github_service.link_issues(pr_obj, response.value)
        try:
            custom_pr
        except NameError:
            custom_pr = pr_obj
        self.call_github_service(github_service_method, github_repo, custom_pr)
