"""Git clone use case."""
import pathlib
import subprocess  # noqa: S404
from typing import List
from typing import Union

import git_portfolio.github_service as ghs
import git_portfolio.response_objects as res
import git_portfolio.use_cases.git_use_case as guc


class GitCloneUseCase:
    """Execution of git clone use case."""

    def __init__(self, github_service: ghs.GithubService) -> None:
        """Constructor."""
        self.github_service = github_service
        self.err_output = guc.GitUseCase.check_command_installed("git")

    def execute(
        self, git_selected_repos: List[str]
    ) -> Union[res.ResponseFailure, res.ResponseSuccess]:
        """Batch `git clone` command.

        Args:
            git_selected_repos: list of configured repo names.

        Returns:
            str: output.
            str: error output.
        """
        if self.err_output:
            return res.ResponseFailure.build_system_error(self.err_output)
        output = ""
        cwd = pathlib.Path().absolute()
        for repo_name in git_selected_repos:
            folder_name = repo_name.split("/")[1]
            clone_path = self.github_service.get_repo_url(repo_name)
            output += f"{folder_name}: "
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
            else:
                error_str = error.decode("utf-8")
                output += f"{error_str}"
        return res.ResponseSuccess(output)
