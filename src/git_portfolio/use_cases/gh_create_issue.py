"""Create issue on Github use case."""
from typing import Union

import git_portfolio.domain.issue as i
import git_portfolio.responses as res
import git_portfolio.use_cases.gh as gh


class GhCreateIssueUseCase(gh.GhUseCase):
    """Github create issue use case."""

    def execute(
        self, issue: i.Issue, github_repo: str = ""
    ) -> Union[res.ResponseFailure, res.ResponseSuccess]:
        """Create issues."""
        output = ""
        if github_repo:
            output = self.call_github_service(
                "create_issue_from_repo", output, github_repo, issue
            )
        else:
            for github_repo in self.config_manager.config.github_selected_repos:
                output = self.call_github_service(
                    "create_issue_from_repo", output, github_repo, issue
                )

        return self.generate_response(output)
