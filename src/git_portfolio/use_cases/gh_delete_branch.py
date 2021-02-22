"""Delete branch on Github use case."""
import git_portfolio.use_cases.gh as gh


class GhDeleteBranchUseCase(gh.GhUseCase):
    """Github delete branch use case."""

    def action(self, github_repo: str, branch: str) -> None:  # type: ignore[override]
        """Delete branches."""
        github_service_method = "delete_branch_from_repo"
        self.call_github_service(github_service_method, github_repo, branch)
