"""User prompting module."""
from typing import Any
from typing import List

import inquirer

import git_portfolio.domain.gh_connection_settings as gcs
import git_portfolio.domain.issue as i
import git_portfolio.domain.pull_request as pr
import git_portfolio.domain.pull_request_merge as prm
import git_portfolio.prompt_validation as val


class InquirerPrompter:
    """Question prompting using inquirer."""

    @staticmethod
    def connect_github(github_access_token: str) -> gcs.GhConnectionSettings:
        """Prompt questions to connect to Github."""
        questions = [
            inquirer.Password(
                "github_access_token",
                message="GitHub access token",
                validate=val.not_empty_validation,
                default=github_access_token,
            ),
            inquirer.Text(
                "github_hostname",
                message="GitHub hostname (change ONLY if you use GitHub Enterprise)",
            ),
        ]
        answers = inquirer.prompt(questions)
        return gcs.GhConnectionSettings(
            answers["github_access_token"], answers["github_hostname"]
        )

    @staticmethod
    def new_repos(github_selected_repos: List[str]) -> Any:
        """Prompt question to know if you want to select new repositories."""
        message = "\nThe configured repos will be used:\n"
        for repo in github_selected_repos:
            message += f" * {repo}\n"
        print(message)
        answer = inquirer.prompt(
            [inquirer.Confirm("", message="Do you want to select new repositories?")]
        )[""]
        return answer

    @staticmethod
    def select_repos(repo_names: List[str]) -> Any:
        """Prompt questions to select new repositories."""
        while True:
            message = "Which repos are you working on? (Select pressing space)"
            selected = inquirer.prompt(
                [
                    inquirer.Checkbox(
                        "github_repos",
                        message=message,
                        choices=repo_names,
                    )
                ]
            )["github_repos"]
            if selected:
                return selected
            else:
                print("Please select with `space` at least one repo.\n")

    @staticmethod
    def create_issues(github_selected_repos: List[str]) -> i.Issue:
        """Prompt questions to create issues."""
        questions = [
            inquirer.Text(
                "title",
                message="Write an issue title",
                validate=val.not_empty_validation,
            ),
            inquirer.Text("body", message="Write an issue body [optional]"),
            inquirer.Text(
                "labels", message="Write issue labels [optional, separated by comma]"
            ),
            inquirer.Confirm(
                "correct",
                message=(
                    "Confirm creation of issue for the project(s) "
                    f"{github_selected_repos}. Continue?"
                ),
                default=False,
            ),
        ]
        correct = False
        while not correct:
            answers = inquirer.prompt(questions)
            correct = answers["correct"]

        labels = (
            set(label.strip() for label in answers["labels"].split(","))
            if answers["labels"]
            else set()
        )
        return i.Issue(answers["title"], answers["body"], labels)

    @staticmethod
    def create_pull_requests(github_selected_repos: List[str]) -> pr.PullRequest:
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
            # inquirer.Confirm(
            #     "draft", message="Do you want to create a draft PR?", default=False
            # ),
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
                default="",
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

        labels = (
            set(label.strip() for label in answers["labels"].split(","))
            if answers["labels"]
            else set()
        )
        return pr.PullRequest(
            answers["title"],
            answers["body"],
            labels,
            answers["confirmation"],
            answers["link"],
            answers["inherit_labels"],
            answers["head"],
            answers["base"],
            False,
        )

    @staticmethod
    def delete_branches(github_selected_repos: List[str]) -> Any:
        """Prompt questions to delete branches."""
        questions = [
            inquirer.Text(
                "branch",
                message="Write the branch name",
                validate=val.not_empty_validation,
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

    @staticmethod
    def merge_pull_requests(
        github_username: str, github_selected_repos: List[str]
    ) -> prm.PullRequestMerge:
        """Prompt questions to merge pull requests."""
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
                "prefix",
                message="Write base user or organization name from PR head",
                default=github_username,
                validate=val.not_empty_validation,
            ),
            inquirer.Confirm(
                "delete_branch",
                message="Do you want to delete head branch on merge?",
                default=False,
            ),
            inquirer.Confirm(
                "correct",
                message=(
                    "Confirm merging of pull request(s) for the project(s) "
                    f"{github_selected_repos}. Continue?"
                ),
                default=False,
            ),
        ]
        correct = False
        while not correct:
            answers = inquirer.prompt(questions)
            correct = answers["correct"]
        return prm.PullRequestMerge(
            answers["base"],
            answers["head"],
            answers["prefix"],
            answers["delete_branch"],
        )
