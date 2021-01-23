"""Base Github use case."""
from typing import Any
from typing import Union

import git_portfolio.config_manager as cm
import git_portfolio.github_service as ghs
import git_portfolio.responses as res


class GhUseCase:
    """Github use case."""

    def __init__(
        self, config_manager: cm.ConfigManager, github_service: ghs.GithubService
    ) -> None:
        """Initializer."""
        self.config_manager = config_manager
        self.github_service = github_service
        self.error = False

    def call_github_service(
        self, method: str, output: str, *args: Any, **kwargs: Any
    ) -> str:
        """Handle error from github_service."""
        try:
            method_to_call = getattr(self.github_service, method)
            output += method_to_call(*args, **kwargs)
        except AttributeError as ae:
            self.error = True
            output += str(ae)
        return output

    def generate_response(
        self, output: str
    ) -> Union[res.ResponseFailure, res.ResponseSuccess]:
        """Create appropriate response object."""
        if self.error:
            return res.ResponseFailure(res.ResponseTypes.PARAMETERS_ERROR, output)
        return res.ResponseSuccess(output)
