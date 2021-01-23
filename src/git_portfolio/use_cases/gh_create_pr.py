"""Create pull request on Github use case."""
from typing import Union

import git_portfolio.domain.pull_request as pr
import git_portfolio.request_objects.issue_list as il
import git_portfolio.responses as res
import git_portfolio.use_cases.gh as gh
import git_portfolio.use_cases.gh_list_issue as li


class GhCreatePrUseCase(gh.GhUseCase):
    """Github merge pull request use case."""

    def execute(
        self,
        pr: pr.PullRequest,
        request_object: Union[il.IssueListValidRequest, il.IssueListInvalidRequest],
        github_repo: str = "",
    ) -> Union[res.ResponseFailure, res.ResponseSuccess]:
        """Create pull requests."""
        output = ""
        if github_repo:
            if pr.link_issues:
                response = li.GhListIssueUseCase(
                    self.config_manager, self.github_service
                ).execute(request_object, github_repo)
                if isinstance(response, res.ResponseSuccess):
                    custom_pr = self.github_service.link_issues(pr, response.value)
                else:
                    custom_pr = pr
            output = self.call_github_service(
                "create_pull_request_from_repo", output, github_repo, pr
            )
        else:
            if pr.link_issues:
                for github_repo in self.config_manager.config.github_selected_repos:
                    response = li.GhListIssueUseCase(
                        self.config_manager, self.github_service
                    ).execute(request_object, github_repo)
                    if isinstance(response, res.ResponseSuccess):
                        custom_pr = self.github_service.link_issues(pr, response.value)
                    else:
                        custom_pr = pr
                    output = self.call_github_service(
                        "create_pull_request_from_repo", output, github_repo, custom_pr
                    )
            else:
                for github_repo in self.config_manager.config.github_selected_repos:
                    output = self.call_github_service(
                        "create_pull_request_from_repo", output, github_repo, pr
                    )
        return self.generate_response(output)
