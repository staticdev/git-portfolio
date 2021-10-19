"""Test cases for git use case."""
import pytest
from pytest_mock import MockerFixture

import git_portfolio.use_cases.git as git


@pytest.fixture
def mock_command_checker(mocker: MockerFixture) -> MockerFixture:
    """Fixture for mocking CommandChecker.check."""
    return mocker.patch("git_portfolio.use_cases.command_checker.CommandChecker.check")


@pytest.fixture
def mock_popen(mocker: MockerFixture) -> MockerFixture:
    """Fixture for mocking subprocess.Popen."""
    mock = mocker.patch("subprocess.Popen")
    mock.return_value.returncode = 0
    mock.return_value.communicate.return_value = (b"some output", b"")
    return mock


def test_execute_success(mock_popen: MockerFixture) -> None:
    """It returns success messages."""
    response = git.GitUseCase().execute(
        ["staticdev/omg", "staticdev/omg2"], "checkout", ("xx",)
    )

    assert bool(response) is True
    assert response.value == "omg: some output\nomg2: some output\n"


def test_execute_success_no_output(mock_popen: MockerFixture) -> None:
    """It returns success message."""
    mock_popen.return_value.communicate.return_value = (b"", b"")
    response = git.GitUseCase().execute(
        ["staticdev/omg", "staticdev/omg2"], "add", (".",)
    )

    assert bool(response) is True
    assert response.value == "omg: add successful.\nomg2: add successful.\n"


def test_execute_git_not_installed(mock_command_checker: MockerFixture) -> None:
    """It returns failure with git not installed message."""
    mock_command_checker.return_value = "error"
    response = git.GitUseCase().execute(["staticdev/notcloned"], "checkout", ("xx",))

    assert bool(response) is False
    assert "error" == response.value["message"]


def test_execute_no_folder(
    mock_command_checker: MockerFixture, mock_popen: MockerFixture
) -> None:
    """It returns that file does not exist."""
    mock_command_checker.return_value = ""
    mock_exception = FileNotFoundError(2, "No such file or directory")
    mock_exception.filename = "/path/x"
    mock_popen.side_effect = mock_exception
    response = git.GitUseCase().execute(["staticdev/x"], "checkout", ("xx",))

    assert bool(response) is True
    assert response.value == "x: No such file or directory: /path/x\n"


def test_execute_error_during_execution(mock_popen: MockerFixture) -> None:
    """It returns success message with the error on output."""
    mock_popen.return_value.returncode = 1
    mock_popen().communicate.return_value = (
        b"",
        b"error: pathspec 'xyz' did not match any file(s) known to git",
    )
    response = git.GitUseCase().execute(["staticdev/notcloned"], "checkout", ("xyz",))

    assert bool(response) is True
    assert (
        response.value
        == "notcloned: error: pathspec 'xyz' did not match any file(s) known to git"
    )
