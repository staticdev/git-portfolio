"""Command-line interface."""
import logging
import sys
from typing import Any
from typing import List
from typing import Optional
from typing import Set
from typing import Union

import github
import requests

import git_portfolio.config_manager as config_manager
import git_portfolio.prompt as prompt

# starting log
FORMAT = "%(asctime)s %(message)s"
DATE_FORMAT = "%d/%m/%Y %H:%M:%S"
logging.basicConfig(level=logging.ERROR, format=FORMAT, datefmt=DATE_FORMAT)
LOGGER = logging.getLogger(__name__)


class PortfolioManager:
    """Portfolio manager class."""

    def __init__(self) -> None:
        """Constructor."""
        self.config_manager = config_manager.ConfigManager()
        self.configs = self.config_manager.load_configs()
        if self.configs.github_access_token:
            self.github_setup()
        else:
            self.config_ini()

    def create_issues(
        self, issue: Optional[prompt.Issue] = None, github_repo: str = ""
    ) -> None:
        """Create issues."""
        if not issue:
            issue = prompt.create_issues(self.configs.github_selected_repos)
        labels = (
            [label.strip() for label in issue.labels.split(",")] if issue.labels else []
        )

        if github_repo:
            self._create_issue_from_repo(github_repo, issue, labels)
        else:
            for github_repo in self.configs.github_selected_repos:
                self._create_issue_from_repo(github_repo, issue, labels)

    def _create_issue_from_repo(
        self, github_repo: str, issue: Any, labels: List[str]
    ) -> None:
        """Create issue from one repository."""
        repo = self.github_connection.get_repo(github_repo)
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

    def create_pull_requests(
        self, pr: Optional[prompt.PullRequest] = None, github_repo: str = ""
    ) -> None:
        """Create pull requests."""
        if not pr:
            pr = prompt.create_pull_requests(self.configs.github_selected_repos)

        if github_repo:
            self._create_pull_request_from_repo(github_repo, pr)
        else:
            for github_repo in self.configs.github_selected_repos:
                self._create_pull_request_from_repo(github_repo, pr)

    def _create_pull_request_from_repo(self, github_repo: str, pr: Any) -> None:
        """Create pull request from one repository."""
        repo = self.github_connection.get_repo(github_repo)
        body = pr.body
        labels = (
            set(label.strip() for label in pr.labels.split(",")) if pr.labels else set()
        )
        if pr.confirmation:
            body = self._link_issues(body, labels, pr, repo)
        try:
            created_pr = repo.create_pull(
                title=pr.title, body=body, head=pr.head, base=pr.base, draft=pr.draft,
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

    def _link_issues(self, body: str, labels: Set[Any], pr: Any, repo: Any) -> Any:
        """Return body message linking issues."""
        issues = repo.get_issues(state="open")
        closes = ""
        for issue in issues:
            if pr.link in issue.title:
                closes += f"#{issue.number} "
                if pr.inherit_labels:
                    issue_labels = [label.name for label in issue.get_labels()]
                    labels.update(issue_labels)
        closes = closes.strip()
        if closes:
            body += f"\n\nCloses {closes}"
        return body

    def merge_pull_requests(
        self, pr_merge: Optional[prompt.PullRequestMerge] = None, github_repo: str = ""
    ) -> None:
        """Merge pull requests."""
        if not pr_merge:
            pr_merge = prompt.merge_pull_requests(
                self.github_username, self.configs.github_selected_repos
            )
        # Important note: base and head arguments have different import formats.
        # https://developer.github.com/v3/pulls/#list-pull-requests
        # head needs format "user/org:branch"
        head = f"{pr_merge.prefix}:{pr_merge.head}"
        state = "open"

        if github_repo:
            self._merge_pull_request_from_repo(github_repo, head, pr_merge, state)
        else:
            for github_repo in self.configs.github_selected_repos:
                self._merge_pull_request_from_repo(github_repo, head, pr_merge, state)

    def _merge_pull_request_from_repo(
        self, github_repo: str, head: str, pr_merge: Any, state: str
    ) -> None:
        """Merge pull request from one repository."""
        repo = self.github_connection.get_repo(github_repo)
        pulls = repo.get_pulls(state=state, base=pr_merge.base, head=head)
        if pulls.totalCount == 1:
            pull = pulls[0]
            if pull.mergeable:
                try:
                    pull.merge()
                    print(f"{github_repo}: PR merged successfully.")
                    if pr_merge.delete_branch:
                        self.delete_branches(pr_merge.head, github_repo)
                except github.GithubException as github_exception:
                    print(f"{github_repo}: {github_exception.data['message']}.")
            else:
                print(
                    (
                        f"{github_repo}: PR not mergeable, GitHub checks may be "
                        "running."
                    )
                )
        else:
            print(
                (
                    f"{github_repo}: no open PR found for {pr_merge.base}:"
                    f"{pr_merge.head}."
                )
            )

    def delete_branches(self, branch: str = "", github_repo: str = "") -> None:
        """Delete branches."""
        if not branch:
            branch = prompt.delete_branches(self.configs.github_selected_repos)

        if github_repo:
            self._delete_branch_from_repo(github_repo, branch)
        else:
            for github_repo in self.configs.github_selected_repos:
                self._delete_branch_from_repo(github_repo, branch)

    def _delete_branch_from_repo(self, github_repo: str, branch: str) -> None:
        """Delete a branch from one repository."""
        repo = self.github_connection.get_repo(github_repo)
        try:
            git_ref = repo.get_git_ref(f"heads/{branch}")
            git_ref.delete()
            print(f"{github_repo}: branch deleted successfully.")
        except github.GithubException as github_exception:
            print(f"{github_repo}: {github_exception.data['message']}.")

    def get_github_connection(self) -> github.Github:
        """Get Github connection."""
        # GitHub Enterprise
        if self.configs.github_hostname:
            base_url = f"https://{self.configs.github_hostname}/api/v3"
            return github.Github(
                base_url=base_url, login_or_token=self.configs.github_access_token
            )
        # GitHub.com
        return github.Github(self.configs.github_access_token)

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
            sys.exit("Unable to reach server. Please check you network.")

    def get_github_repos(
        self,
        user: Union[
            github.AuthenticatedUser.AuthenticatedUser, github.NamedUser.NamedUser
        ],
    ) -> Any:
        """Get Github repos from user."""
        return user.get_repos()

    def config_repos(self) -> None:
        """Configure repos in use."""
        if self.configs.github_selected_repos:
            print("\nThe configured repos will be used:")
            for repo in self.configs.github_selected_repos:
                print(" *", repo)
            new_repos = prompt.new_repos()
            if not new_repos:
                print("gitp successfully configured.")
                return

        repo_names = [repo.full_name for repo in self.github_repos]

        self.configs.github_selected_repos = prompt.select_repos(repo_names)
        self.config_manager.save_configs(self.configs)
        print("gitp successfully configured.")

    def github_setup(self) -> bool:
        """Setup Github connection properties."""
        self.github_connection = self.get_github_connection()
        user = self.github_connection.get_user()
        self.github_username = self.get_github_username(user)
        if not self.github_username:
            return False
        self.github_repos = self.get_github_repos(user)
        return True

    def config_ini(self) -> None:
        """Initialize app configuration."""
        # only config if gets a valid connection
        valid = False
        while not valid:
            answers = prompt.connect_github(self.configs.github_access_token)
            self.configs.github_access_token = answers.github_access_token.strip()
            self.configs.github_hostname = answers.github_hostname
            valid = self.github_setup()
            if not valid:
                print("Wrong GitHub token/permissions. Please try again.")
        self.config_repos()
