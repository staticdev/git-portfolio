"""Create issue on Github use case."""
from typing import Any
from typing import List
from typing import Optional

import github
import inquirer

import git_portfolio.github_manager as ghm
import git_portfolio.prompt_validation as val
from git_portfolio.domain.issue import Issue


def prompt_create_issues(github_selected_repos: List[str]) -> Issue:
    """Prompt questions to create issues."""
    questions = [
        inquirer.Text(
            "title", message="Write an issue title", validate=val.not_empty_validation
        ),
        inquirer.Text("body", message="Write an issue body [optional]"),
        inquirer.Text(
            "labels", message="Write issue labels [optional, separated by comma]"
        ),
        inquirer.Confirm(
            "correct",
            message=(
                f"Confirm creation of issue for the project(s) {github_selected_repos}"
                ". Continue?"
            ),
            default=False,
        ),
    ]
    correct = False
    while not correct:
        answers = inquirer.prompt(questions)
        correct = answers["correct"]
    return Issue(answers["title"], answers["body"], answers["labels"])


class GhCreateIssueUseCase:
    """Github create issue use case."""

    def __init__(self, github_manager: ghm.GithubManager) -> None:
        """Initializer."""
        self.github_manager = github_manager

    def execute(self, issue: Optional[Issue] = None, github_repo: str = "") -> None:
        """Create issues."""
        if not issue:
            issue = prompt_create_issues(
                self.github_manager.config.github_selected_repos
            )
        labels = (
            [label.strip() for label in issue.labels.split(",")] if issue.labels else []
        )

        if github_repo:
            self._create_issue_from_repo(github_repo, issue, labels)
        else:
            for github_repo in self.github_manager.config.github_selected_repos:
                self._create_issue_from_repo(github_repo, issue, labels)

    def _create_issue_from_repo(
        self, github_repo: str, issue: Any, labels: List[str]
    ) -> None:
        """Create issue from one repository."""
        repo = self.github_manager.github_connection.get_repo(github_repo)
        try:
            repo.create_issue(title=issue.title, body=issue.body, labels=labels)
            print(f"{github_repo}: issue created successfully.")
        except github.GithubException as github_exception:
            if github_exception.data["message"] == "Issues are disabled for this repo":
                print(
                    (
                        f"{github_repo}: {github_exception.data['message']}. "
                        "It may be a fork."
                    )
                )
            else:
                print(f"{github_repo}: {github_exception.data['message']}.")
