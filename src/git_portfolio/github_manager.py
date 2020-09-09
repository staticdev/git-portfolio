"""Command-line interface."""
import logging
import sys
from typing import Any
from typing import List
from typing import Optional
from typing import Union

import github
import inquirer
import requests

import git_portfolio.config_manager as cm
import git_portfolio.prompt_validation as val
from git_portfolio.domain.gh_connection_settings import GhConnectionSettings

# starting log
FORMAT = "%(asctime)s %(message)s"
DATE_FORMAT = "%d/%m/%Y %H:%M:%S"
logging.basicConfig(level=logging.ERROR, format=FORMAT, datefmt=DATE_FORMAT)
LOGGER = logging.getLogger(__name__)


def prompt_connect_github(github_access_token: str) -> GhConnectionSettings:
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
    return GhConnectionSettings(
        answers["github_access_token"], answers["github_hostname"]
    )


def prompt_new_repos(github_selected_repos: List[str]) -> Any:
    """Prompt question to know if you want to select new repositories."""
    message = "\nThe configured repos will be used:\n"
    for repo in github_selected_repos:
        message += f" * {repo}\n"
    print(message)
    answer = inquirer.prompt(
        [inquirer.Confirm("", message="Do you want to select new repositories?")]
    )[""]
    return answer


def prompt_select_repos(repo_names: List[str]) -> Any:
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


class GithubManager:
    """Github manager class."""

    def __init__(self, config: cm.Config) -> None:
        """Constructor."""
        self.config = config
        if config.github_access_token:
            self._github_setup()
        else:
            self.config_ini()

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
            sys.exit(
                (
                    "Unable to reach server. Please check you network and credentials "
                    "and try again."
                )
            )

    def _get_github_repos(
        self,
        user: Union[
            github.AuthenticatedUser.AuthenticatedUser, github.NamedUser.NamedUser
        ],
    ) -> Any:
        """Get Github repos from user."""
        return user.get_repos()

    def config_ini(self) -> None:
        """Initialize app configuration."""
        # only config if gets a valid connection
        valid = False
        while not valid:
            answers = prompt_connect_github(self.config.github_access_token)
            self.config.github_access_token = answers.github_access_token.strip()
            self.config.github_hostname = answers.github_hostname
            valid = self._github_setup()
            if not valid:
                print("Wrong GitHub token/permissions. Please try again.")
        self.config_repos()

    def config_repos(self) -> Optional[cm.Config]:
        """Configure repos in use."""
        if self.config.github_selected_repos:
            new_repos = prompt_new_repos(self.config.github_selected_repos)
            if not new_repos:
                return None

        repo_names = [repo.full_name for repo in self.github_repos]
        self.config.github_selected_repos = prompt_select_repos(repo_names)
        return self.config

    def _github_setup(self) -> bool:
        """Setup Github connection properties."""
        self.github_connection = self.get_github_connection()
        user = self.github_connection.get_user()
        self.github_username = self.get_github_username(user)
        if not self.github_username:
            return False
        self.github_repos = self._get_github_repos(user)
        return True
