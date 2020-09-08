"""Create pull request on Github use case."""
from typing import Any
from typing import List
from typing import Optional
from typing import Set

import github
import inquirer

import git_portfolio.github_manager as ghm
import git_portfolio.prompt_validation as val
from git_portfolio.domain.pull_request import PullRequest


def prompt_create_pull_requests(github_selected_repos: List[str]) -> PullRequest:
    """Prompt questions to create pull requests."""
    questions = [
        inquirer.Text(
            "base",
            message="Write base branch name (destination)",
            default="master",
            validate=val.not_empty_validation,
        ),
        inquirer.Text(
            "head",
            message="Write the head branch name (source)",
            validate=val.not_empty_validation,
        ),
        inquirer.Text(
            "title", message="Write a PR title", validate=val.not_empty_validation
        ),
        inquirer.Text("body", message="Write an PR body [optional]"),
        inquirer.Confirm(
            "draft", message="Do you want to create a draft PR?", default=False
        ),
        inquirer.Text(
            "labels", message="Write PR labels [optional, separated by comma]"
        ),
        inquirer.Confirm(
            "confirmation",
            message="Do you want to link pull request to issues by title?",
            default=False,
        ),
        inquirer.Text(
            "link",
            message="Write issue title (or part of it)",
            validate=val.not_empty_validation,
            ignore=val.ignore_if_not_confirmed,
        ),
        inquirer.Confirm(
            "inherit_labels",
            message="Do you want to add labels inherited from the issues?",
            default=True,
            ignore=val.ignore_if_not_confirmed,
        ),
        inquirer.Confirm(
            "correct",
            message=(
                "Confirm creation of pull request(s) for the project(s) "
                f"{github_selected_repos}. Continue?"
            ),
            default=False,
        ),
    ]
    correct = False
    while not correct:
        answers = inquirer.prompt(questions)
        correct = answers["correct"]
    return PullRequest(
        answers["title"],
        answers["body"],
        answers["labels"],
        answers["confirmation"],
        answers["link"],
        answers["inherit_labels"],
        answers["head"],
        answers["base"],
        answers["draft"],
    )


class GhCreatePrUseCase:
    """Github merge pull request use case."""

    def __init__(self, github_manager: ghm.GithubManager) -> None:
        """Initializer."""
        self.github_manager = github_manager

    def execute(self, pr: Optional[PullRequest] = None, github_repo: str = "") -> None:
        """Create pull requests."""
        if not pr:
            pr = prompt_create_pull_requests(
                self.github_manager.config.github_selected_repos
            )

        if github_repo:
            self._create_pull_request_from_repo(github_repo, pr)
        else:
            for github_repo in self.github_manager.config.github_selected_repos:
                self._create_pull_request_from_repo(github_repo, pr)

    def _create_pull_request_from_repo(self, github_repo: str, pr: Any) -> None:
        """Create pull request from one repository."""
        repo = self.github_manager.github_connection.get_repo(github_repo)
        body = pr.body
        labels = (
            set(label.strip() for label in pr.labels.split(",")) if pr.labels else set()
        )
        if pr.confirmation:
            body = self._link_issues(body, labels, pr, repo)
        try:
            created_pr = repo.create_pull(
                title=pr.title,
                body=body,
                head=pr.head,
                base=pr.base,
                draft=pr.draft,
            )
            print(f"{github_repo}: PR created successfully.")
            # PyGithub does not support a list of strings for adding (only one str)
            for label in labels:
                created_pr.add_to_labels(label)
        except github.GithubException as github_exception:
            extra = ""
            for error in github_exception.data["errors"]:
                if "message" in error:
                    extra += f"{error['message']} "  # type: ignore
                else:
                    extra += f"Invalid field {error['field']}. "  # type: ignore
            print(f"{github_repo}: {github_exception.data['message']}. {extra}")

    @staticmethod
    def _link_issues(body: str, labels: Set[Any], pr: Any, repo: Any) -> Any:
        """Return body message linking issues."""
        issues = repo.get_issues(state="open")
        closes = ""
        for issue in issues:
            if pr.link in issue.title:
                closes += f"Closes #{issue.number}\n"
                if pr.inherit_labels:
                    issue_labels = [label.name for label in issue.get_labels()]
                    labels.update(issue_labels)
        if closes:
            body += f"\n\n{closes}"
        return body
