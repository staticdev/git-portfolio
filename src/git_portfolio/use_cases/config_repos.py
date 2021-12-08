"""Config repositories use case."""
from __future__ import annotations

import git_portfolio.config_manager as cm
import git_portfolio.domain.gh_connection_settings as cs
import git_portfolio.responses as res


class ConfigReposUseCase:
    """Gitp config repositories use case."""

    def __init__(self, config_manager: cm.ConfigManager) -> None:
        """Initializer."""
        self.config_manager = config_manager

    def execute(
        self, github_config: cs.GhConnectionSettings, selected_repos: list[str]
    ) -> res.Response:
        """Configuration of git repositories."""
        self.config_manager.config.github_access_token = github_config.access_token
        self.config_manager.config.github_hostname = github_config.hostname
        self.config_manager.config.github_selected_repos = selected_repos
        self.config_manager.save_config()
        return res.ResponseSuccess("gitp repositories successfully configured.")
