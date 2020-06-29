"""Command-line interface."""
import logging
import sys
from typing import Any
from typing import Dict
from typing import Optional

import github
import requests

import git_portfolio.config_manager
import git_portfolio.prompt


# starting log
FORMAT = "%(asctime)s %(message)s"
DATE_FORMAT = "%d/%m/%Y %H:%M:%S"
logging.basicConfig(level=logging.ERROR, format=FORMAT, datefmt=DATE_FORMAT)
LOGGER = logging.getLogger(__name__)


class GithubManager:
    def __init__(self):
        self.github_repos = []
        self.github_connection = None
        self.config_manager = git_portfolio.config_manager.ConfigManager()
        self.configs = self.config_manager.load_configs()

    def create_issues(self, issue: Optional[git_portfolio.prompt.Issue] = None) -> None:
        if not issue:
            issue = git_portfolio.prompt.create_issues(self.configs.github_selected_repos)
        labels = (
            [label.strip() for label in issue.labels.split(",")]
            if issue.labels
            else []
        )
        for github_repo in self.configs.github_selected_repos:
            repo = self.github_connection.get_repo(github_repo)
            try:
                repo.create_issue(
                    title=issue.title, body=issue.body, labels=labels
                )
                print("{}: issue created successfully.".format(github_repo))
            except github.GithubException as github_exception:
                if (
                    github_exception.data["message"]
                    == "Issues are disabled for this repo"
                ):
                    print(
                        "{}: {}. It may be a fork.".format(
                            github_repo, github_exception.data["message"]
                        )
                    )
                else:
                    print(
                        "{}: {}.".format(
                            github_repo, github_exception.data["message"]
                        )
                    )

    def create_pull_requests(self, pr: Optional[git_portfolio.prompt.PullRequest] = None) -> None:
        if not pr:
            pr = git_portfolio.prompt.create_pull_requests(self.configs.github_selected_repos)

        for github_repo in self.configs.github_selected_repos:
            repo = self.github_connection.get_repo(github_repo)
            body = pr.body
            labels = (
                set(label.strip() for label in pr.labels.split(","))
                if pr.labels
                else set()
            )
            # link issues
            if pr.confirmation:
                issues = repo.get_issues(state="open")
                closes = ""
                for issue in issues:
                    if pr.link in issue.title:
                        closes += "#{} ".format(issue.number)
                        if pr.inherit_labels:
                            issue_labels = [
                                label.name for label in issue.get_labels()
                            ]
                            labels.update(issue_labels)
                closes = closes.strip()
                if closes:
                    body += "\n\nCloses {}".format(closes)
            try:
                pr = repo.create_pull(
                    title=pr.title,
                    body=body,
                    head=pr.head,
                    base=pr.base,
                    draft=pr.draft,
                )
                print("{}: PR created successfully.".format(github_repo))
                # PyGithub does not support a list of strings for adding (only one str)
                for label in labels:
                    pr.add_to_labels(label)
            except github.GithubException as github_exception:
                extra = ""
                for error in github_exception.data["errors"]:
                    if "message" in error:
                        extra += "{} ".format(error["message"])
                    else:
                        extra += "Invalid field {}. ".format(error["field"])
                print(
                    "{}: {}. {}".format(
                        github_repo, github_exception.data["message"], extra
                    )
                )

    def merge_pull_requests(self) -> None:
        """Merge pull request."""
        state = "open"
        pr_merge = git_portfolio.prompt.merge_pull_requests()
        # Important note: base and head arguments have different import formats.
        # https://developer.github.com/v3/pulls/#list-pull-requests
        # head needs format "user/org:branch"
        head = "{}:{}".format(pr_merge.prefix, pr_merge.head)

        for github_repo in self.configs.github_selected_repos:
            repo = self.github_connection.get_repo(github_repo)
            pulls = repo.get_pulls(state=state, base=pr_merge.base, head=head)
            if pulls.totalCount == 1:
                pull = pulls[0]
                if pull.mergeable:
                    try:
                        pull.merge()
                        print("{}: PR merged successfully.".format(github_repo))
                    except github.GithubException as github_exception:
                        print(
                            "{}: {}.".format(
                                github_repo, github_exception.data["message"]
                            )
                        )
                else:
                    print(
                        "{}: PR not mergeable, GitHub checks may be running.".format(
                            github_repo
                        )
                    )
            else:
                print(
                    "{}: no open PR found for {}:{}.".format(
                        github_repo, pr_merge.base, pr_merge.head
                    )
                )

    def delete_branches(self, branch="") -> None:
        if not branch:
            branch = git_portfolio.prompt.delete_branches(self.configs.github_selected_repos)

        for github_repo in self.configs.github_selected_repos:
            repo = self.github_connection.get_repo(github_repo)
            try:
                git_ref = repo.get_git_ref("heads/{}".format(branch))
                git_ref.delete()
                print("{}: branch deleted successfully.".format(github_repo))
            except github.GithubException as github_exception:
                print(
                    "{}: {}.".format(github_repo, github_exception.data["message"])
                )

    def init_config(self) -> None:
        answers = git_portfolio.prompt.connect_github(self.configs.github_access_token)
        self.configs.github_access_token = answers.github_access_token.strip()
        # GitHub Enterprise
        if answers.github_hostname:
            base_url = "https://{}/api/v3".format(answers.github_hostname)
            self.github_connection = github.Github(
                base_url=base_url, login_or_token=self.configs.github_access_token
            )
        # GitHub.com
        else:
            self.github_connection = github.Github(self.configs.github_access_token)
        user = self.github_connection.get_user()
        try:
            self.github_username = user.login
        except (github.BadCredentialsException, github.GithubException):
            print("Wrong GitHub token/permissions. Please try again.")
            return self.connect_github()
        except requests.exceptions.ConnectionError:
            sys.exit("Unable to reach server. Please check you network.")
        self.github_repos = user.get_repos()
        self.select_github_repos()

    def select_github_repos(self) -> None:
        if self.configs.github_selected_repos:
            print("\nThe configured repos will be used:")
            for repo in self.configs.github_selected_repos:
                print(" *", repo)
            new_repos = git_portfolio.prompt.new_repos()
            if not new_repos:
                print("gitp successfully configured.")
                return

        try:
            repo_names = [repo.full_name for repo in self.github_repos]
        except Exception as ex:
            print(ex)

        self.configs.github_selected_repos = git_portfolio.prompt.select_repos(repo_names)
        self.config_manager.save_configs(self.configs)
        print("gitp successfully configured.")
