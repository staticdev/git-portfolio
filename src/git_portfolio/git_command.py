"""Local git commands."""
import os
import pathlib
import subprocess  # noqa: S404
from typing import List
from typing import Tuple


class GitCommand:
    """Execution of git commands."""

    def __init__(self) -> None:
        """Constructor."""
        self.err_output = self._check_git_install()

    @staticmethod
    def _check_git_install() -> str:
        popen = subprocess.Popen(  # noqa: S603, S607
            "git", stdout=subprocess.DEVNULL, stderr=subprocess.PIPE
        )
        _, error = popen.communicate()
        if error:
            return "This command requires Git executable installed and on system path."
        return ""

    def execute(
        self, git_selected_repos: List[str], command: str, args: Tuple[str]
    ) -> Tuple[str, str]:
        """Batch `git` command.

        Args:
            git_selected_repos: list of configured repo names.
            command: supported: checkout.
            args (Tuple[str]): command arguments.

        Returns:
            str: output.
            str: error output.
        """
        if self.err_output:
            return "", self.err_output
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
                if stdout:
                    stdout_str = stdout.decode("utf-8")
                    output += f"{stdout_str}"
                if error:
                    error_str = error.decode("utf-8")
                    output += f"{error_str}"
            except FileNotFoundError as fnf_error:
                output += f"{fnf_error}\n"
            except Exception as ex:
                print(ex)
        return output, ""
