"""Test cases for the git command module."""
from typing import Any

import pytest
from pytest_mock import MockerFixture

from git_portfolio import git_command as gc


@pytest.fixture
def mock_popen(mocker: MockerFixture) -> Any:
    """Fixture for mocking subprocess.Popen."""
    mock = mocker.patch("subprocess.Popen")
    mock.return_value.communicate.return_value = (b"checked out successfully.\n", b"")
    return mock


def test_checkout_success(mock_popen: MockerFixture) -> None:
    """It returns success messages."""
    stdout, err = gc.GitCommand().execute(
        ["staticdev/omg", "staticdev/omg2"], "checkout", ("xx",)
    )
    assert stdout == "omg: checked out successfully.\nomg2: checked out successfully.\n"
    assert not err


def test_checkout_no_folder() -> None:
    """It returns in stdout that file does not exist."""
    stdout, err = gc.GitCommand().execute(["staticdev/notcloned"], "checkout", ("xx",))
    assert "notcloned" and "No such file or directory" in stdout
    assert err == ""
