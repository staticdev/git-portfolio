"""Config model."""
from typing import List


class Config:
    """Config class."""

    def __init__(
        self,
        github_hostname: str,
        github_access_token: str,
        github_selected_repos: List[str],
    ):
        """Constructor."""
        self.github_hostname = github_hostname
        self.github_access_token = github_access_token
        self.github_selected_repos = github_selected_repos
