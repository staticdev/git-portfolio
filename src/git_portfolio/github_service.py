"""Github service module."""
from __future__ import annotations

import abc
import copy
from typing import Any

import github3

import git_portfolio.domain.gh_connection_settings as cs
import git_portfolio.domain.issue as i
import git_portfolio.domain.pull_request as pr
import git_portfolio.domain.pull_request_merge as prm
import git_portfolio.request_objects.issue_list as il


class GithubServiceError(Exception):
    """Generic error for GithubService."""

    pass


class AbstractGithubService(abc.ABC):
    """Abstract Github service class."""

    @abc.abstractmethod
    def list_issues_from_repo(
        self,
        github_repo: str,
        request: il.IssueListValidRequest | il.IssueListInvalidRequest,
    ) -> list[i.Issue]:
        """Return list of issues from one repository."""
        raise NotImplementedError  # pragma: no cover

    @staticmethod
    @abc.abstractmethod
    def link_issues(
        pr_base: pr.PullRequest, filtered_issues: list[i.Issue]
    ) -> pr.PullRequest:
        """Return a new PR with body message and labels of linked issues."""
        raise NotImplementedError  # pragma: no cover


class GithubService(AbstractGithubService):
    """Github service class."""

    def __init__(self, github_config: cs.GhConnectionSettings) -> None:
        """Constructor."""
        self.config = github_config
        self.connection = self._get_connection()
        self.user = self._test_connection(self.connection)
        self.repos = self.connection.repositories()

    def _get_connection(self) -> github3.GitHub | github3.GitHubEnterprise:
        """Get Github connection, create one if does not exist."""
        if hasattr(self, "connection"):
            return self.connection

        # GitHub Enterprise
        if self.config.hostname:
            base_url = f"https://{self.config.hostname}/api/v3"
            return github3.enterprise_login(
                url=base_url, token=self.config.access_token
            )
        # GitHub.com
        else:
            return github3.login(token=self.config.access_token)

    @staticmethod
    def _test_connection(
        connection: github3.GitHub | github3.GitHubEnterprise,
    ) -> github3.users.AuthenticatedUser:
        """Test connection by returning user."""
        try:
            return connection.me()
        except github3.exceptions.AuthenticationFailed:
            raise GithubServiceError(
                "Wrong GitHub permissions. Please check your token."
            ) from None
        except github3.exceptions.ConnectionError as github_error:
            raise GithubServiceError(
                "Unable to reach server. Please check your network and credentials. "
                "This also happens when Github is offline, then try again later."
            ) from github_error
        except github3.exceptions.IncompleteResponse:
            raise GithubServiceError(
                "Invalid response. Your token might not be properly scoped."
            ) from None

    def _get_repo(self, repo_name: str) -> github3.repos.ShortRepository:
        for repo in self.repos:
            if repo.full_name == repo_name:
                return repo
        raise NameError(f"Repository {repo_name} not found.") from None

    def get_config(self) -> cs.GhConnectionSettings:
        """Get service config."""
        return self.config

    def get_repo_names(self) -> list[str]:
        """Get list of repository names."""
        return [repo.full_name for repo in self.repos]

    def get_repo_url(self, repo_name: str) -> str:
        """Get URL for repo."""
        for repo in self.repos:
            if repo.full_name == repo_name:
                host = self.config.hostname if self.config.hostname else "github.com"
                return f"git@{host}:{repo.full_name}.git"
        raise NameError(f"Repository {repo_name} not found.")

    def get_username(self) -> Any:
        """Get Github username."""
        return self.user.login

    def create_issue_from_repo(self, github_repo: str, issue: i.Issue) -> str:
        """Create issue from one repository."""
        repo = self._get_repo(github_repo)
        try:
            repo.create_issue(
                title=issue.title, body=issue.body, labels=list(issue.labels)
            )
            return f"{github_repo}: create issue successful.\n"
        except github3.exceptions.ClientError as client_error:
            if client_error.msg == "Issues are disabled for this repo":
                return f"{github_repo}: {client_error.msg}. It may be a fork.\n"
            else:
                return f"{github_repo}: {client_error.msg}.\n"
        except github3.exceptions.GitHubError as github_error:
            raise GithubServiceError(
                f"{github_repo}: {github_error.msg}\n"
            ) from github_error

    def list_issues_from_repo(
        self,
        github_repo: str,
        request: il.IssueListValidRequest | il.IssueListInvalidRequest,
    ) -> list[i.Issue]:
        """Return list of issues from one repository."""
        if isinstance(request, il.IssueListValidRequest):
            repo = self._get_repo(github_repo)

            domain_issues = []
            if not request.filters:
                issues = list(repo.issues())
                for issue in issues:
                    labels = {label.name for label in issue.labels()}
                    domain_issues.append(
                        i.Issue(issue.number, issue.title, issue.body, labels)
                    )
                return issues

            obj = request.filters.get("obj__eq")
            state = request.filters.get("state__eq")
            title_query = request.filters.get("title__contains")
            issues = list(repo.issues(state=state))

            if obj == "issue":
                issues = [issue for issue in issues if issue.pull_request_urls is None]
            elif obj == "pull request":
                issues = [issue for issue in issues if issue.pull_request_urls]

            if title_query:
                issues = [issue for issue in issues if title_query in issue.title]

            for issue in issues:
                labels = {label.name for label in issue.labels()}
                domain_issues.append(
                    i.Issue(issue.number, issue.title, issue.body, labels)
                )

            return domain_issues
        return []

    def close_issues_from_repo(
        self, github_repo: str, domain_issues: list[i.Issue]
    ) -> str:
        """Close issues from one repository."""
        connection = self._get_connection()
        repo_suffix = github_repo.split("/")[1]

        if not domain_issues:
            return f"{github_repo}: no issues match.\n"

        for domain_issue in domain_issues:
            issue = connection.issue(
                self.get_username(), repo_suffix, domain_issue.number
            )
            if not issue.is_closed():
                issue.close()
        return f"{github_repo}: close issues successful.\n"

    def reopen_issues_from_repo(
        self, github_repo: str, domain_issues: list[i.Issue]
    ) -> str:
        """Reopen issues from one repository."""
        connection = self._get_connection()
        repo_suffix = github_repo.split("/")[1]

        if not domain_issues:
            return f"{github_repo}: no issues match.\n"

        for domain_issue in domain_issues:
            issue = connection.issue(
                self.get_username(), repo_suffix, domain_issue.number
            )
            issue.reopen()
        return f"{github_repo}: reopen issues successful.\n"

    def create_pull_request_from_repo(
        self, github_repo: str, pr: pr.PullRequest
    ) -> str:
        """Create pull request from one repository."""
        repo = self._get_repo(github_repo)
        try:
            # github3 does not have draft attribute
            # watch https://github.com/sigmavirus24/github3.py/issues/926
            created_pr = repo.create_pull(
                title=pr.title,
                body=pr.body,
                head=pr.head,
                base=pr.base,
                # draft=pr.draft,
            )
            if pr.labels:
                issue = created_pr.issue()
                issue.add_labels(*pr.labels)
            return f"{github_repo}: create PR successful.\n"
        except github3.exceptions.UnprocessableEntity as github_exception:
            extra = ""
            for error in github_exception.errors:
                if "message" in error:
                    extra += f" {error['message']}."
                else:
                    extra += f" Invalid field {error['field']}."
            return f"{github_repo}: {github_exception.msg}.{extra}\n"
        except github3.exceptions.GitHubError as github_error:
            raise GithubServiceError(
                f"{github_repo}: {github_error.msg}\n"
            ) from github_error

    @staticmethod
    def link_issues(
        pr_base: pr.PullRequest, filtered_issues: list[i.Issue]
    ) -> pr.PullRequest:
        """Return a new PR with body message and labels of linked issues."""
        pr = copy.deepcopy(pr_base)
        labels = pr.labels
        closes = ""
        for issue in filtered_issues:
            closes += f"Closes #{issue.number}\n"
            issue_labels = list(issue.labels)
            labels.update(issue_labels)
        if closes:
            pr.body += f"\n\n{closes}"
        pr.labels = labels
        return pr

    def delete_branch_from_repo(self, github_repo: str, branch: str) -> str:
        """Delete a branch from one repository."""
        repo = self._get_repo(github_repo)
        try:
            branch_ref = repo.ref(f"heads/{branch}")
            branch_ref.delete()
            return f"{github_repo}: delete branch successful.\n"
        except github3.exceptions.NotFoundError as github_exception:
            return f"{github_repo}: {github_exception.msg}.\n"
        except github3.exceptions.GitHubError as github_error:
            raise GithubServiceError(
                f"{github_repo}: {github_error.msg}\n"
            ) from github_error

    def merge_pull_request_from_repo(
        self, github_repo: str, pr_merge: prm.PullRequestMerge
    ) -> str:
        """Merge pull request from one repository."""
        repo = self._get_repo(github_repo)

        # Important note: base and head arguments have different import formats.
        # https://developer.github.com/v3/pulls/#list-pull-requests
        # head needs format "user/org:branch"
        head = f"{pr_merge.prefix}:{pr_merge.head}"
        pulls = list(repo.pull_requests(base=pr_merge.base, head=head))
        if not pulls:
            raise GithubServiceError(
                f"{github_repo}: no open PR found for "
                f"{pr_merge.base}:{pr_merge.head}.\n"
            )
        elif len(pulls) == 1:
            pull = pulls[0]
            output = ""
            try:
                pull.merge()
                output += f"{github_repo}: merge PR successful.\n"
                return output
            except github3.exceptions.MethodNotAllowed as github_exception:
                raise GithubServiceError(
                    f"{github_repo}: {github_exception.msg}\n"
                ) from github_exception
        else:
            return (
                f"{github_repo}: unexpected number of PRs for "
                f"{pr_merge.base}:{pr_merge.head}.\n"
            )
