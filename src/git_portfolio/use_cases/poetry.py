"""Poetry use case."""
from __future__ import annotations

import os
import pathlib
import subprocess  # noqa: S404
from typing import Union

import git_portfolio.responses as res
import git_portfolio.use_cases.command_checker as command_checker


class PoetryUseCase:
    """Execution of poetry use case."""

    def __init__(self) -> None:
        """Constructor."""
        self.err_output = command_checker.CommandChecker().check("poetry")

    def execute(
        self, git_selected_repos: list[str], command: str, args: tuple[str]
    ) -> Union[res.ResponseFailure, res.ResponseSuccess]:
        """Batch `poetry` command.

        Args:
            git_selected_repos: list of configured repo names.
            command: poetry command eg. install, version, update...
            args: command arguments.

        Returns:
            Union[res.ResponseFailure, res.ResponseSuccess]: final result.
        """
        if self.err_output:
            return res.ResponseFailure(res.ResponseTypes.SYSTEM_ERROR, self.err_output)
        output = ""
        cwd = pathlib.Path().absolute()
        for repo_name in git_selected_repos:
            folder_name = repo_name.split("/")[1]
            output += f"{folder_name}: "
            try:
                popen = subprocess.Popen(  # noqa: S603, S607
                    [command, *args],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=os.path.join(cwd, folder_name),
                )
                stdout, error = popen.communicate()
                if popen.returncode == 0:
                    # case for command with no output on success
                    if not stdout:
                        output += f"{command} successful.\n"
                    else:
                        stdout_str = stdout.decode("utf-8")
                        output += f"{stdout_str}\n"
                else:
                    error_str = error.decode("utf-8")
                    output += f"{error_str}"
            except FileNotFoundError as fnf_error:
                output += f"{fnf_error.strerror}: {fnf_error.filename}\n"
        return res.ResponseSuccess(output)
