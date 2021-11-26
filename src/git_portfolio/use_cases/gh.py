"""Base Github use case."""
import traceback
from typing import Any
from typing import Union

import git_portfolio.config_manager as cm
import git_portfolio.github_service as ghs
import git_portfolio.responses as res


class GhUseCase:
    """Github use case."""

    def __init__(
        self,
        config_manager: cm.ConfigManager,
        github_service: ghs.GithubService,
        github_repo: str = "",
    ) -> None:
        """Initializer."""
        self.config_manager = config_manager
        self.github_service = github_service
        self.error = False
        self.github_repo = github_repo
        self.output = ""

    def call_github_service(self, method: str, *args: Any, **kwargs: Any) -> None:
        """Handle error from github_service."""
        try:
            method_to_call = getattr(self.github_service, method)
            self.output += method_to_call(*args, **kwargs)
        except ghs.GithubServiceError as gse:
            self.error = True
            self.output += str(gse)
        except Exception:
            self.error = True
            self.output += (
                "An unexpected error occured. Please report at "
                "https://github.com/staticdev/git-portfolio/issues/new "
                f"with the following info:\n{traceback.format_exc()}"
            )

    def generate_response(self) -> Union[res.ResponseFailure, res.ResponseSuccess]:
        """Create appropriate response object."""
        if self.error:
            return res.ResponseFailure(res.ResponseTypes.PARAMETERS_ERROR, self.output)
        return res.ResponseSuccess(self.output)

    def action(self, github_repo: str, *args: Any, **kwargs: Any) -> None:
        """Execute some action in a repo."""
        raise NotImplementedError  # pragma: no cover

    def execute(
        self, *args: Any, **kwargs: Any
    ) -> Union[res.ResponseFailure, res.ResponseSuccess]:
        """Execute GitHubUseCase."""
        if self.github_repo:
            self.action(self.github_repo, *args, **kwargs)
        else:
            for github_repo in self.config_manager.config.github_selected_repos:
                self.action(github_repo, *args, **kwargs)
        return self.generate_response()
