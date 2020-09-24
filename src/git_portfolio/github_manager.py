"""Command-line interface."""
import logging
import sys
from typing import Any
from typing import List
from typing import Union

import github
import requests

import git_portfolio.domain.config as c
import git_portfolio.prompt as p


# starting log
FORMAT = "%(asctime)s %(message)s"
DATE_FORMAT = "%d/%m/%Y %H:%M:%S"
logging.basicConfig(level=logging.ERROR, format=FORMAT, datefmt=DATE_FORMAT)
LOGGER = logging.getLogger(__name__)


class GithubManager:
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
