"""Delete branch on Github use case."""
import github

import git_portfolio.github_manager as ghm


class GhDeleteBranchUseCase:
    """Github delete branch use case."""

    def __init__(self, github_manager: ghm.GithubManager) -> None:
        """Initializer."""
        self.github_manager = github_manager

    def execute(self, branch: str, github_repo: str = "") -> None:
        """Delete branches."""
        if github_repo:
            self._delete_branch_from_repo(github_repo, branch)
        else:
            for github_repo in self.github_manager.config.github_selected_repos:
                self._delete_branch_from_repo(github_repo, branch)

    def _delete_branch_from_repo(self, github_repo: str, branch: str) -> None:
        """Delete a branch from one repository."""
        repo = self.github_manager.github_connection.get_repo(github_repo)
        try:
            git_ref = repo.get_git_ref(f"heads/{branch}")
            git_ref.delete()
            print(f"{github_repo}: branch deleted successfully.")
        except github.GithubException as github_exception:
            print(f"{github_repo}: {github_exception.data['message']}.")
