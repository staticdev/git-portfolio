"""Github service module."""
from typing import Any
from typing import List
from typing import Union

import github3

import git_portfolio.domain.gh_connection_settings as cs
import git_portfolio.domain.issue as i
import git_portfolio.domain.pull_request as pr
import git_portfolio.domain.pull_request_merge as prm


class GithubService:
    """Github service class."""

    def __init__(self, github_config: cs.GhConnectionSettings) -> None:
        """Constructor."""
        self.config = github_config
        self.connection = self._get_connection(self.config)
        self.user = self._test_connection(self.connection)
        self.repos = self.connection.repositories()

    def _get_connection(
        self, github_config: cs.GhConnectionSettings
    ) -> Union[github3.GitHub, github3.GitHubEnterprise]:
        """Get Github connection, create one if does not exist."""
        # GitHub Enterprise
        if github_config.hostname:
            base_url = f"https://{github_config.hostname}/api/v3"
            self.connection = github3.enterprise_login(
                url=base_url, token=github_config.access_token
            )
        # GitHub.com
        else:
            self.connection = github3.login(token=github_config.access_token)
        return self.connection

    @staticmethod
    def _test_connection(
        connection: Union[github3.GitHub, github3.GitHubEnterprise]
    ) -> github3.users.AuthenticatedUser:
        """Test connection by returning user."""
        try:
            return connection.me()
        except github3.exceptions.AuthenticationFailed:
            raise AttributeError("Invalid token.")
        except github3.exceptions.ConnectionError:
            raise ConnectionError()
        except github3.exceptions.IncompleteResponse:
            raise AttributeError(
                "Invalid response. Your token might not be properly scoped."
            )

    def _get_repo(self, repo_name: str) -> github3.repos.ShortRepository:
        for repo in self.repos:
            if repo.full_name == repo_name:
                return repo
        raise NameError(f"Repository {repo_name} not found.")

    def get_config(self) -> cs.GhConnectionSettings:
        """Get service config."""
        return self.config

    def get_repo_names(self) -> List[str]:
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
        except github3.exceptions.ClientError as github_exception:
            if github_exception.msg == "Issues are disabled for this repo":
                return f"{github_repo}: {github_exception.msg}. It may be a fork."
            else:
                return f"{github_repo}: {github_exception.msg}."

    # def close_issue_from_repo(self):
    #     print(dir(issue))
    #     if not issue.is_closed():
    #         issue.close()

    # def reopen_issue_from_repo(self):
    #     issue = gh.issue(user, repo, num)
    #     if issue.is_closed():
    #         issue.reopen()

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
            return f"{github_repo}: {github_exception.msg}.{extra}"

    def link_issues(self, github_repo: str, pr: pr.PullRequest) -> None:
        """Set body message and labels on PR."""
        repo = self._get_repo(github_repo)
        labels = pr.labels
        issues = repo.issues(state="open")
        closes = ""
        for issue in issues:
            if pr.link in issue.title:
                closes += f"Closes #{issue.number}\n"
                issue_labels = [label.name for label in issue.labels()]
                labels.update(issue_labels)
        if closes:
            pr.body += f"\n\n{closes}"
        pr.labels = labels

    def delete_branch_from_repo(self, github_repo: str, branch: str) -> str:
        """Delete a branch from one repository."""
        repo = self._get_repo(github_repo)
        try:
            branch_ref = repo.ref(f"heads/{branch}")
            branch_ref.delete()
            return f"{github_repo}: delete branch successful.\n"
        except github3.exceptions.NotFoundError as github_exception:
            return f"{github_repo}: {github_exception.msg}."

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
            return (
                f"{github_repo}: no open PR found for {pr_merge.base}:{pr_merge.head}."
            )
        elif len(pulls) == 1:
            pull = pulls[0]
            output = ""
            pull.merge()
            output += f"{github_repo}: merge PR successful.\n"
            return output
        else:
            return (
                f"{github_repo}: unexpected number of PRs for "
                f"{pr_merge.base}:{pr_merge.head}."
            )
