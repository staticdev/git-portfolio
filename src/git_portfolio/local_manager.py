"""Local git commands."""
from typing import List
from typing import Tuple

import git


class LocalManager:
    """Local repositories manager class."""

    # TODO handle create_head OSError already exists
    def checkout(self, git_selected_repos: List[str], args: Tuple[str]) -> str:
        """Batch `git checkout` command.

        Args:
            git_selected_repos: list of configured repo names.
            args (Tuple[str]): command arguments.

        Returns:
            str: output.
        """
        head = args[0]
        output = ""
        for repo_name in git_selected_repos:
            folder_name = repo_name.split("/")[1]
            try:
                repo = git.Repo(f"./{folder_name}")
                repo.create_head(head).checkout()
                output += f"{folder_name}: checked out successfully.\n"
            except git.exc.NoSuchPathError as git_error:
                output += f"{folder_name}: path {git_error} not found.\n"
        return output
