"""Git status use case."""
import os
import pathlib
import subprocess  # noqa: S404
from typing import List
from typing import Tuple
from typing import Union

import git_portfolio.response_objects as res
import git_portfolio.use_cases.git_use_case as guc


class GitStatusUseCase:
    """Execution of git status use case."""

    def __init__(self) -> None:
        """Constructor."""
        self.err_output = guc.GitUseCase.check_git_install()

    def execute(
        self, git_selected_repos: List[str], args: Tuple[str]
    ) -> Union[res.ResponseFailure, res.ResponseSuccess]:
        """Batch `git status` command.

        Args:
            git_selected_repos: list of configured repo names.
            args: command arguments.

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
            output += f"{folder_name}: "
            try:
                popen = subprocess.Popen(  # noqa: S603, S607
                    ["git", "status", *args],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=os.path.join(cwd, folder_name),
                )
                stdout, _ = popen.communicate()
                stdout_str = stdout.decode("utf-8")
                output += f"{stdout_str}\n"
            except FileNotFoundError as fnf_error:
                output += f"{fnf_error.strerror}: {fnf_error.filename}\n"
        return res.ResponseSuccess(output)
