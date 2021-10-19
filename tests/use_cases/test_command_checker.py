"""Test cases for the command checker use case."""
import pytest
from pytest_mock import MockerFixture

import git_portfolio.use_cases.command_checker as command_checker


@pytest.fixture
def mock_popen(mocker: MockerFixture) -> MockerFixture:
    """Fixture for mocking subprocess.Popen."""
    mock = mocker.patch("subprocess.Popen")
    mock.return_value.returncode = 0
    mock.return_value.communicate.return_value = (b"some output", b"")
    return mock


def test_check_command_installed_success(mock_popen: MockerFixture) -> None:
    """It returns success."""
    response = command_checker.CommandChecker().check("program")

    assert "" == response


def test_check_command_installed_error(mock_popen: MockerFixture) -> None:
    """It returns failure with git not installed message."""
    mock_popen.side_effect = FileNotFoundError
    response = command_checker.CommandChecker().check("program")

    assert (
        "This command requires program executable installed and on system path."
        == response
    )
