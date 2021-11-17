"""Local git use case."""
from __future__ import annotations

import os
import pathlib
import subprocess  # noqa: S404

import git_portfolio.responses as res
import git_portfolio.use_cases.command_checker as command_checker


class GitUseCase:
    """Execution of git use case."""

    def __init__(self) -> None:
        """Constructor."""
        self.err_output = command_checker.CommandChecker().check("git")

    def execute(
        self, git_selected_repos: list[str], command: str, args: tuple[str, ...]
    ) -> res.ResponseFailure | res.ResponseSuccess:
        """Batch `git` command.

        Args:
            git_selected_repos: list of configured repo names.
            command: git command eg. checkout, pull, push...
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
                    ["git", command, *args],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=os.path.join(cwd, folder_name),
                )
                stdout, error = popen.communicate()
                if popen.returncode == 0:
                    if stdout:
                        stdout_str = stdout.decode("utf-8")
                        output += f"{stdout_str}\n"
                    else:
                        output += f"{command} successful.\n"
                else:
                    if error:
                        error_str = error.decode("utf-8")
                        output += f"{error_str}"
                    else:
                        stdout_str = stdout.decode("utf-8")
                        output += f"{stdout_str}\n"
            except FileNotFoundError as fnf_error:
                output += f"{fnf_error.strerror}: {fnf_error.filename}\n"
        return res.ResponseSuccess(output)
