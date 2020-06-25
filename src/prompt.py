"""Prompt module."""
import collections
from typing import Any
from typing import Dict

import inquirer


def _ignore_if_not_confirmed(answers: Dict[str, Any]) -> bool:
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


def delete_branches(github_selected_repos) -> str:
    questions = [
        inquirer.Text(
            "branch",
            message="Write the branch name",
            validate=_not_empty_validation,
        ),
        inquirer.Confirm(
            "correct",
            message="Confirm deleting of branch(es) for the project(s) {}. Continue?".format(
                github_selected_repos
            ),
            default=False,
        ),
    ]
    correct = False
    while not correct:
        answers = inquirer.prompt(questions)
        correct = answers["correct"]
    return answers["branch"]


ConnectGithubAnswers = collections.namedtuple("ConnectGithubAnswers", ["github_access_token", "github_hostname"])


def connect_github(github_access_token: str) -> ConnectGithubAnswers:
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
    return ConnectGithubAnswers(answers["github_access_token"], answers["github_hostname"])


def new_repo() -> bool:
    answer = inquirer.prompt(
                [
                    inquirer.Confirm(
                        "", message="Do you want to select new repositories?"
                    )
                ]
            )[""]
    return answer
