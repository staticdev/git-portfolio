"""Local git use case."""
from __future__ import annotations

import os
import pathlib
import subprocess  # noqa: S404

import git_portfolio.responses as res
import git_portfolio.use_cases.command_checker as command_checker


class GitUseCase:
    """Execution of git use case."""

    def execute(
        self, git_selected_repos: list[str], command: str, args: tuple[str, ...]
    ) -> list[res.Response]:
        """Batch `git` command.

        Args:
            git_selected_repos: list of configured repo names.
            command: git command eg. checkout, pull, push...
            args: command arguments.

        Returns:
            list[res.Response]: final results.
        """
        err_output = command_checker.CommandChecker().check("git")
        if err_output:
            return [res.ResponseFailure(res.ResponseTypes.SYSTEM_ERROR, err_output)]
        responses: list[res.Response] = []
        cwd = pathlib.Path().absolute()
        for repo_name in git_selected_repos:
            folder_name = repo_name.split("/")[1]
            output = f"{folder_name}: "
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
                    responses.append(res.ResponseSuccess(output))
                else:
                    if error:
                        error_str = error.decode("utf-8")
                        output += f"{error_str}"
                        responses.append(
                            res.ResponseFailure(
                                res.ResponseTypes.RESOURCE_ERROR, output
                            )
                        )
                    else:
                        stdout_str = stdout.decode("utf-8")
                        output += f"{stdout_str}\n"
                        responses.append(res.ResponseSuccess(output))
            except FileNotFoundError as fnf_error:
                output += f"{fnf_error.strerror}: {fnf_error.filename}\n"
                responses.append(
                    res.ResponseFailure(res.ResponseTypes.RESOURCE_ERROR, output)
                )
        return responses
