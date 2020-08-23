"""Test cases for the local manager module."""
from unittest.mock import Mock
from unittest.mock import patch

import git

from git_portfolio import local_manager as lm


@patch("git.Repo", autospec=True)
def test_checkout_success(mock_git_repo: Mock) -> None:
    """It returns success messages."""
    assert (
        lm.LocalManager().checkout(["staticdev/omg", "staticdev/omg2"], ("xx",))
        == "omg: checked out successfully.\nomg2: checked out successfully.\n"
    )


@patch("git.Repo", autospec=True)
def test_checkout_error(mock_git_repo: Mock) -> None:
    """It returns error as output."""
    mock_git_repo.side_effect = git.exc.NoSuchPathError("/path")
    assert (
        lm.LocalManager().checkout(["staticdev/notcloned"], ("xx",))
        == "notcloned: path /path not found.\n"
    )
