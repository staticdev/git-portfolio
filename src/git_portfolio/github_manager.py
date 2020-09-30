"""Command-line interface."""
import logging
import sys
from typing import Any
from typing import List
from typing import Union

import github
import requests

import git_portfolio.domain.config as c
import git_portfolio.domain.issue as i
import git_portfolio.domain.pull_request as pr
import git_portfolio.domain.pull_request_merge as prm
import git_portfolio.prompt as p


# starting log
FORMAT = "%(asctime)s %(message)s"
DATE_FORMAT = "%d/%m/%Y %H:%M:%S"
logging.basicConfig(level=logging.ERROR, format=FORMAT, datefmt=DATE_FORMAT)
LOGGER = logging.getLogger(__name__)


class GithubService:
    """Github manager class."""

    def __init__(self, config: c.Config) -> None:
        """Constructor."""
        self.config = config
        if config.github_access_token:
            self._validate_account()

    def get_github_connection(self) -> github.Github:
        """Get Github connection."""
        # GitHub Enterprise
        if self.config.github_hostname:
            base_url = f"https://{self.config.github_hostname}/api/v3"
            return github.Github(
                base_url=base_url, login_or_token=self.config.github_access_token
            )
        # GitHub.com
        return github.Github(self.config.github_access_token)

    def get_github_username(
        self,
        user: Union[
            github.AuthenticatedUser.AuthenticatedUser, github.NamedUser.NamedUser
        ],
    ) -> str:
        """Get Github username."""
        try:
            return user.login
        except (github.BadCredentialsException, github.GithubException):
            return ""
        except requests.exceptions.ConnectionError:
            raise ConnectionError()
            sys.exit(
                (
                    "Unable to reach server. Please check you network and credentials "
                    "and try again."
                )
            )

    def get_repo_names(self) -> List[str]:
        """Get list of repository names."""
        return [repo.full_name for repo in self.github_repos]

    def _get_github_repos(
        self,
        user: Union[
            github.AuthenticatedUser.AuthenticatedUser, github.NamedUser.NamedUser
        ],
    ) -> Any:
        """Get Github repos from user."""
        return user.get_repos()

    def _validate_account(self) -> bool:
        """Validate Github connection properties."""
        self.github_connection = self.get_github_connection()
        user = self.github_connection.get_user()
        self.github_username = self.get_github_username(user)
        if not self.github_username:
            return False
        self.github_repos = self._get_github_repos(user)
        return True

    def set_github_account(self) -> None:
        """Set Github properties."""
        valid = False
        while not valid:
            answers = p.InquirerPrompter.connect_github(self.config.github_access_token)
            self.config.github_access_token = answers.github_access_token.strip()
            self.config.github_hostname = answers.github_hostname
            valid = self._validate_account()
            if not valid:
                print("Wrong GitHub token/permissions. Please try again.")

    def create_issue_from_repo(self, github_repo: str, issue: i.Issue) -> str:
        """Create issue from one repository."""
        repo = self.github_connection.get_repo(github_repo)
        try:
            repo.create_issue(
                title=issue.title, body=issue.body, labels=list(issue.labels)
            )
            return f"{github_repo}: issue created successfully."
        except github.GithubException as github_exception:
            if github_exception.data["message"] == "Issues are disabled for this repo":
                return (
                    f"{github_repo}: {github_exception.data['message']}. "
                    "It may be a fork."
                )

            else:
                return f"{github_repo}: {github_exception.data['message']}."

    def create_pull_request_from_repo(
        self, github_repo: str, pr: pr.PullRequest
    ) -> str:
        """Create pull request from one repository."""
        repo = self.github_connection.get_repo(github_repo)
        try:
            created_pr = repo.create_pull(
                title=pr.title,
                body=pr.body,
                head=pr.head,
                base=pr.base,
                draft=pr.draft,
            )
            # PyGithub does not support a list of strings for adding (only one str)
            for label in pr.labels:
                created_pr.add_to_labels(label)
            return f"{github_repo}: PR created successfully."
        except github.GithubException as github_exception:
            extra = ""
            for error in github_exception.data["errors"]:
                if "message" in error:
                    extra += f"{error['message']} "  # type: ignore
                else:
                    extra += f"Invalid field {error['field']}. "  # type: ignore
            return f"{github_repo}: {github_exception.data['message']}. {extra}"

    def link_issues(self, github_repo: str, pr: pr.PullRequest) -> None:
        """Set body message and labels on PR."""
        repo = self.github_connection.get_repo(github_repo)
        labels = pr.labels
        issues = repo.get_issues(state="open")
        closes = ""
        for issue in issues:
            if pr.link in issue.title:
                closes += f"Closes #{issue.number}\n"
                if pr.inherit_labels:
                    issue_labels = [label.name for label in issue.get_labels()]
                    labels.update(issue_labels)
        if closes:
            pr.body += f"\n\n{closes}"
        pr.labels = labels

    def delete_branch_from_repo(self, github_repo: str, branch: str) -> str:
        """Delete a branch from one repository."""
        repo = self.github_connection.get_repo(github_repo)
        try:
            git_ref = repo.get_git_ref(f"heads/{branch}")
            git_ref.delete()
            return f"{github_repo}: branch deleted successfully."
        except github.GithubException as github_exception:
            return f"{github_repo}: {github_exception.data['message']}."

    def merge_pull_request_from_repo(
        self, github_repo: str, pr_merge: prm.PullRequestMerge
    ) -> str:
        """Merge pull request from one repository."""
        repo = self.github_connection.get_repo(github_repo)

        # Important note: base and head arguments have different import formats.
        # https://developer.github.com/v3/pulls/#list-pull-requests
        # head needs format "user/org:branch"
        head = f"{pr_merge.prefix}:{pr_merge.head}"
        pulls = repo.get_pulls(state="open", base=pr_merge.base, head=head)
        if pulls.totalCount == 1:
            pull = pulls[0]
            if pull.mergeable:
                output = ""
                try:
                    pull.merge()
                    output += f"{github_repo}: PR merged successfully.\n"
                except github.GithubException as github_exception:
                    output += f"{github_repo}: {github_exception.data['message']}."
                return output
            else:
                return f"{github_repo}: PR not mergeable, GitHub checks may be running."
        else:
            return (
                f"{github_repo}: no open PR found for {pr_merge.base}:"
                f"{pr_merge.head}."
            )
