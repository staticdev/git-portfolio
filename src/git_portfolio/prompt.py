"""Prompt module."""
import collections
from typing import Any
from typing import Dict
from typing import List

import inquirer


def _ignore_if_not_confirmed(answers: Dict[str, Any]) -> bool:
    """Ignore if not confirmed question."""
    return not answers["confirmation"]


def _not_empty_validation(answers: Dict[str, Any], current: str) -> bool:
    """Validade if current answer is not just spaces.

    Args:
        answers (Dict[str, Any]): answers to previous questions (ignored).
        current (str): answer to current question.

    Returns:
        bool: if is valid output.
    """
    current_without_spaces = current.strip()
    return True if current_without_spaces else False


Issue = collections.namedtuple("Issue", ["title", "body", "labels"])


def create_issues(github_selected_repos: List[str]) -> Issue:
    """Prompt questions to create issues."""
    questions = [
        inquirer.Text(
            "title", message="Write an issue title", validate=_not_empty_validation
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


def delete_branches(github_selected_repos: List[str]) -> Any:
    """Prompt questions to delete branches."""
    questions = [
        inquirer.Text(
            "branch", message="Write the branch name", validate=_not_empty_validation
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


PullRequest = collections.namedtuple(
    "PullRequest",
    [
        "title",
        "body",
        "labels",
        "confirmation",
        "link",
        "inherit_labels",
        "head",
        "base",
        "draft",
    ],
)


def create_pull_requests(github_selected_repos: List[str]) -> PullRequest:
    """Prompt questions to create pull requests."""
    questions = [
        inquirer.Text(
            "base",
            message="Write base branch name (destination)",
            default="master",
            validate=_not_empty_validation,
        ),
        inquirer.Text(
            "head",
            message="Write the head branch name (source)",
            validate=_not_empty_validation,
        ),
        inquirer.Text(
            "title", message="Write a PR title", validate=_not_empty_validation
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
            validate=_not_empty_validation,
            ignore=_ignore_if_not_confirmed,
        ),
        inquirer.Confirm(
            "inherit_labels",
            message="Do you want to add labels inherited from the issues?",
            default=True,
            ignore=_ignore_if_not_confirmed,
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


PullRequestMerge = collections.namedtuple(
    "PullRequestMerge", ["base", "head", "prefix", "delete_branch"]
)


def merge_pull_requests(
    github_username: str, github_selected_repos: List[str]
) -> PullRequestMerge:
    """Prompt questions to merge pull requests."""
    questions = [
        inquirer.Text(
            "base",
            message="Write base branch name (destination)",
            default="master",
            validate=_not_empty_validation,
        ),
        inquirer.Text(
            "head",
            message="Write the head branch name (source)",
            validate=_not_empty_validation,
        ),
        inquirer.Text(
            "prefix",
            message="Write base user or organization name from PR head",
            default=github_username,
            validate=_not_empty_validation,
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
    return PullRequestMerge(
        answers["base"], answers["head"], answers["prefix"], answers["delete_branch"]
    )


ConnectGithub = collections.namedtuple(
    "ConnectGithub", ["github_access_token", "github_hostname"]
)


def connect_github(github_access_token: str) -> ConnectGithub:
    """Prompt questions to connect to Github."""
    questions = [
        inquirer.Password(
            "github_access_token",
            message="GitHub access token",
            validate=_not_empty_validation,
            default=github_access_token,
        ),
        inquirer.Text(
            "github_hostname",
            message="GitHub hostname (change ONLY if you use GitHub Enterprise)",
        ),
    ]
    answers = inquirer.prompt(questions)
    return ConnectGithub(answers["github_access_token"], answers["github_hostname"])


def new_repos() -> Any:
    """Prompt question to know if you want to select new repositories."""
    answer = inquirer.prompt(
        [inquirer.Confirm("", message="Do you want to select new repositories?")]
    )[""]
    return answer


def select_repos(repo_names: List[str]) -> Any:
    """Prompt questions to select new repositories."""
    while True:
        selected = inquirer.prompt(
            [
                inquirer.Checkbox(
                    "github_repos",
                    message="Which repos are you working on? (Select pressing space)",
                    choices=repo_names,
                )
            ]
        )["github_repos"]
        if selected:
            return selected
        else:
            print("Please select with `space` at least one repo.\n")
