"""Initialize config use case."""
from typing import Union

import git_portfolio.config_manager as cm
import git_portfolio.github_manager as ghm
import git_portfolio.prompt as p
import git_portfolio.response_objects as res
import git_portfolio.use_cases.config_repos_use_case as cr


class ConfigInitUseCase:
    """Gitp config initialization use case."""

    def __init__(
        self, config_manager: cm.ConfigManager, github_manager: ghm.GithubManager
    ) -> None:
        """Initializer."""
        self.config_manager = config_manager
        self.github_manager = github_manager

    def execute(self) -> Union[res.ResponseFailure, res.ResponseSuccess]:
        """Initialize app configuration."""
        self.github_manager.set_github_account()
        repo_names = self.github_manager.get_repo_names()
        selected_repos = p.InquirerPrompter.select_repos(repo_names)
        cr.ConfigReposUseCase(self.config_manager).execute(selected_repos)
        return res.ResponseSuccess("gitp successfully configured.")
