"""Create issue on Github use case."""
import git_portfolio.domain.issue as i
import git_portfolio.use_cases.gh as gh


class GhCreateIssueUseCase(gh.GhUseCase):
    """Github create issue use case."""

    def action(  # type: ignore[override]
        self, github_repo: str, issue: i.Issue
    ) -> None:
        """Create issues."""
        github_service_method = "create_issue_from_repo"
        self.call_github_service(github_service_method, github_repo, issue)
