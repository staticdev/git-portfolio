"""Git clone use case."""
from __future__ import annotations

import pathlib
import subprocess  # noqa: S404

import git_portfolio.github_service as ghs
import git_portfolio.responses as res
import git_portfolio.use_cases.command_checker as command_checker


class GitCloneUseCase:
    """Execution of git clone use case."""

    def __init__(self, github_service: ghs.GithubService) -> None:
        """Constructor."""
        self.github_service = github_service
        self.err_output = command_checker.CommandChecker().check("git")

    def execute(self, git_selected_repos: list[str]) -> list[res.Response]:
        """Batch `git clone` command.

        Args:
            git_selected_repos: list of configured repo names.

        Returns:
            list[res.Response]: final results.
        """
        if self.err_output:
            return [
                res.ResponseFailure(res.ResponseTypes.SYSTEM_ERROR, self.err_output)
            ]
        responses: list[res.Response] = []
        cwd = pathlib.Path().absolute()
        for repo_name in git_selected_repos:
            folder_name = repo_name.split("/")[1]
            clone_path = self.github_service.get_repo_url(repo_name)
            output = f"{folder_name}: "
            popen = subprocess.Popen(  # noqa: S603, S607
                ["git", "clone", clone_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=cwd,
            )
            _, error = popen.communicate()
            # check for errors
            if popen.returncode == 0:
                output += "clone successful.\n"
                responses.append(res.ResponseSuccess(output))
            else:
                error_str = error.decode("utf-8")
                output += f"{error_str}"
                responses.append(
                    res.ResponseFailure(res.ResponseTypes.RESOURCE_ERROR, output)
                )
        return responses
