"""Poetry use case."""
from __future__ import annotations

import os
import pathlib
import subprocess  # noqa: S404

import git_portfolio.responses as res
import git_portfolio.use_cases.command_checker as command_checker


class PoetryUseCase:
    """Execution of poetry use case."""

    def execute(
        self, git_selected_repos: list[str], command: str, args: tuple[str]
    ) -> res.ResponseFailure | res.ResponseSuccess:
        """Batch `poetry` command.

        Args:
            git_selected_repos: list of configured repo names.
            command: poetry command eg. install, version, update...
            args: command arguments.

        Returns:
            res.ResponseFailure | res.ResponseSuccess: final result.
        """
        err_output = command_checker.CommandChecker().check("poetry")
        if err_output:
            return res.ResponseFailure(res.ResponseTypes.SYSTEM_ERROR, err_output)
        output = ""
        error = False
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
                stdout, err = popen.communicate()
                if popen.returncode == 0:
                    # case for command with no output on success
                    if not stdout:
                        output += f"{command} successful.\n"
                    else:
                        stdout_str = stdout.decode("utf-8")
                        output += f"{stdout_str}\n"
                else:
                    error = True
                    error_str = err.decode("utf-8")
                    output += f"{error_str}"
            except FileNotFoundError as fnf_error:
                error = True
                output += f"{fnf_error.strerror}: {fnf_error.filename}\n"
        if error:
            return res.ResponseFailure(res.ResponseTypes.PARAMETERS_ERROR, output)
        return res.ResponseSuccess(output)
