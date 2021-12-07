"""Merge pull request on Github use case."""
import git_portfolio.domain.pull_request_merge as prm
import git_portfolio.use_cases.gh as gh
import git_portfolio.use_cases.gh_delete_branch as dbr


class GhMergePrUseCase(gh.GhUseCase):
    """Github merge pull request use case."""

    def action(  # type: ignore[override]
        self,
        github_repo: str,
        pr_merge: prm.PullRequestMerge,
    ) -> None:
        """Merge pull requests."""
        github_service_method = "merge_pull_request_from_repo"
        resp = self.call_github_service(github_service_method, github_repo, pr_merge)
        if pr_merge.delete_branch and bool(resp):
            delete_branch_use_case = dbr.GhDeleteBranchUseCase(
                self.config_manager, self.github_service
            )
            delete_branch_use_case.execute(pr_merge.head)
