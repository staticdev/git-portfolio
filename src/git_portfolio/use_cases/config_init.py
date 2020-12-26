"""Initialize config use case."""
from typing import Union

import git_portfolio.config_manager as cm
import git_portfolio.domain.gh_connection_settings as gcs
import git_portfolio.github_service as ghs
import git_portfolio.prompt as p
import git_portfolio.responses as res
import git_portfolio.use_cases.config_repos as cr


class ConfigInitUseCase:
    """Gitp config initialization use case."""

    def __init__(self, config_manager: cm.ConfigManager) -> None:
        """Initializer."""
        self.config_manager = config_manager

    def execute(
        self, request: gcs.GhConnectionSettings
    ) -> Union[res.ResponseFailure, res.ResponseSuccess]:
        """Initialize app configuration."""
        try:
            new_github_service = ghs.GithubService(request)
        except AttributeError as ae:
            return res.ResponseFailure(res.ResponseTypes.PARAMETERS_ERROR, f"{ae}")
        except ConnectionError:
            return res.ResponseFailure(
                res.ResponseTypes.SYSTEM_ERROR,
                "impossible to connect, please check your hostname address and token.",
            )
        repo_names = new_github_service.get_repo_names()
        config = new_github_service.get_config()
        selected_repos = p.InquirerPrompter.select_repos(repo_names)
        cr.ConfigReposUseCase(self.config_manager).execute(config, selected_repos)
        return res.ResponseSuccess("gitp successfully configured.")
