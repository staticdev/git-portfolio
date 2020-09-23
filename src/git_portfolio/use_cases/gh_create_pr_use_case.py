"""Create pull request on Github use case."""
from typing import Any
from typing import Optional
from typing import Set

import github

import git_portfolio.github_manager as ghm
import git_portfolio.prompt as p
from git_portfolio.domain.pull_request import PullRequest


class GhCreatePrUseCase:
    """Github merge pull request use case."""

    def __init__(self, github_manager: ghm.GithubManager) -> None:
        """Initializer."""
        self.github_manager = github_manager

    def execute(self, pr: Optional[PullRequest] = None, github_repo: str = "") -> None:
        """Create pull requests."""
        if not pr:
            pr = p.create_pull_requests(
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
