"""Base Github use case."""
from __future__ import annotations

import traceback
from typing import Any

import git_portfolio.config_manager as cm
import git_portfolio.github_service as gs
import git_portfolio.responses as res


class GhUseCase:
    """Github use case."""

    def __init__(
        self,
        config_manager: cm.ConfigManager,
        github_service: gs.AbstractGithubService,
        github_repo: str = "",
    ) -> None:
        """Initializer."""
        self.config_manager = config_manager
        self.github_service = github_service
        self.github_repo = github_repo
        self.responses: list[res.Response] = []

    def call_github_service(
        self, method: str, *args: Any, **kwargs: Any
    ) -> res.Response:
        """Handle error from github_service and return response."""
        response: res.Response
        try:
            method_to_call = getattr(self.github_service, method)
            output = method_to_call(*args, **kwargs)
            response = res.ResponseSuccess(output)
        except gs.GithubServiceError as gse:
            response = res.ResponseFailure(res.ResponseTypes.RESOURCE_ERROR, str(gse))
        except Exception:
            error_msg = (
                "An unexpected error occured. Please report at "
                "https://github.com/staticdev/git-portfolio/issues/new "
                f"with the following info:\n{traceback.format_exc()}"
            )
            response = res.ResponseFailure(res.ResponseTypes.SYSTEM_ERROR, error_msg)
        self.responses.append(response)
        return response

    def action(self, github_repo: str, *args: Any, **kwargs: Any) -> None:
        """Execute some action in a repo."""
        raise NotImplementedError  # pragma: no cover

    def execute(self, *args: Any, **kwargs: Any) -> list[res.Response]:
        """Execute GitHubUseCase."""
        if self.github_repo:
            self.action(self.github_repo, *args, **kwargs)
        else:
            for github_repo in self.config_manager.config.github_selected_repos:
                self.action(github_repo, *args, **kwargs)
        return self.responses
