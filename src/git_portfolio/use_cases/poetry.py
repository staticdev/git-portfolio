"""Poetry use case."""
from __future__ import annotations

import os
import pathlib
import subprocess  # nosec

import git_portfolio.responses as res
import git_portfolio.use_cases.command_checker as command_checker


class PoetryUseCase:
    """Execution of poetry use case."""

    def execute(
        self, git_selected_repos: list[str], command: str, args: tuple[str, ...]
    ) -> list[res.Response]:
        """Batch `poetry` command.

        Args:
            git_selected_repos: list of configured repo names.
            command: poetry command eg. install, version, update...
            args: command arguments.

        Returns:
            list[res.Response]: final results.
        """
        err_output = command_checker.CommandChecker().check("poetry")
        if err_output:
            return [res.ResponseFailure(res.ResponseTypes.SYSTEM_ERROR, err_output)]
        responses: list[res.Response] = []
        cwd = pathlib.Path().absolute()
        for repo_name in git_selected_repos:
            folder_name = repo_name.split("/")[1]
            output = f"{folder_name}: "
            try:
                popen = subprocess.Popen(  # nosec
                    # --ansi option makes output with colors
                    [command, *args, "--ansi"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=os.path.join(cwd, folder_name),
                )
                stdout, _ = popen.communicate()
                stdout_str = stdout.decode("utf-8")
                output += f"{stdout_str}"
                if popen.returncode == 0:
                    responses.append(res.ResponseSuccess(output))
                else:
                    responses.append(
                        res.ResponseFailure(res.ResponseTypes.RESOURCE_ERROR, output)
                    )
            except FileNotFoundError as fnf_error:
                output += f"{fnf_error.strerror}: {fnf_error.filename}\n"
                responses.append(
                    res.ResponseFailure(res.ResponseTypes.RESOURCE_ERROR, output)
                )
        return responses
