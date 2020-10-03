"""Github service module."""
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
        self.connection = self._get_connection(github_config)
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
            raise AttributeError()
        except github3.exceptions.ConnectionError:
            raise ConnectionError()

    def _get_repo(self, repo_name: str) -> github3.repos.ShortRepository:
        for repo in self.repos:
            if repo.full_name == repo_name:
                return repo

    def get_repo_names(self) -> List[str]:
        """Get list of repository names."""
        return [str(repo) for repo in self.repos]

    def get_username(self) -> str:
        """Get Github username."""
        return str(self.user)

    def create_issue_from_repo(self, github_repo: str, issue: i.Issue) -> str:
        """Create issue from one repository."""
        repo = self._get_repo(github_repo)
        try:
            repo.create_issue(
                title=issue.title, body=issue.body, labels=list(issue.labels)
            )
            return f"{github_repo}: issue created successfully."
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
        except github3.exceptions.ClientError as github_exception:
            extra = ""
            for error in github_exception.data["errors"]:
                if "message" in error:
                    extra += f"{error['message']} "
                else:
                    extra += f"Invalid field {error['field']}. "
            return f"{github_repo}: {github_exception.data['message']}. {extra}"

    def link_issues(self, github_repo: str, pr: pr.PullRequest) -> None:
        """Set body message and labels on PR."""
        repo = self._get_repo(github_repo)
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
        repo = self._get_repo(github_repo)
        try:
            # TODO: watch https://github.com/sigmavirus24/github3.py/issues/1002
            branch_ref = repo.branch(branch)
            print(dir(branch_ref))
            branch_ref.delete()
            return f"{github_repo}: branch deleted successfully."
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
        pulls = repo.get_pulls(state="open", base=pr_merge.base, head=head)
        if pulls.totalCount == 1:
            pull = pulls[0]
            if pull.mergeable:
                output = ""
                try:
                    pull.merge()
                    output += f"{github_repo}: PR merged successfully.\n"
                except github3.exceptions.ClientError as github_exception:
                    output += f"{github_repo}: {github_exception.data['message']}."
                return output
            else:
                return f"{github_repo}: PR not mergeable, GitHub checks may be running."
        else:
            return (
                f"{github_repo}: no open PR found for {pr_merge.base}:"
                f"{pr_merge.head}."
            )
