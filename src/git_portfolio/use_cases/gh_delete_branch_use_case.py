"""Delete branch on Github use case."""
from typing import Any
from typing import List

import github
import inquirer

import git_portfolio.github_manager as ghm
import git_portfolio.prompt_validation as val


def prompt_delete_branches(github_selected_repos: List[str]) -> Any:
    """Prompt questions to delete branches."""
    questions = [
        inquirer.Text(
            "branch", message="Write the branch name", validate=val.not_empty_validation
        ),
        inquirer.Confirm(
            "correct",
            message=(
                "Confirm deleting of branch(es) for the project(s) "
                f"{github_selected_repos}. Continue?"
            ),
            default=False,
        ),
    ]
    correct = False
    while not correct:
        answers = inquirer.prompt(questions)
        correct = answers["correct"]
    return answers["branch"]


class GhDeleteBranchUseCase:
    """Github delete branch use case."""

    def __init__(self, github_manager: ghm.GithubManager) -> None:
        """Initializer."""
        self.github_manager = github_manager

    def execute(self, branch: str = "", github_repo: str = "") -> None:
        """Delete branches."""
        if not branch:
            branch = prompt_delete_branches(
                self.github_manager.config.github_selected_repos
            )

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
