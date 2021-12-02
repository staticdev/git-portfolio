"""Test cases for poetry use case."""
import pytest
from pytest_mock import MockerFixture

import git_portfolio.use_cases.poetry as poetry


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


def test_execute_success(
    mock_popen: MockerFixture, mock_command_checker: MockerFixture
) -> None:
    """It returns success messages."""
    mock_command_checker.return_value = ""
    response = poetry.PoetryUseCase().execute(
        ["user/repo", "user/repo2"], "poetry", ("version",)
    )

    assert bool(response) is True
    assert response.value == "repo: some output\nrepo2: some output\n"


# TODO: this is only to maintain logic from git use case
# no known poetry command has no output when merging
# with GitUseCase remove this non-sense example.
def test_execute_success_no_output(mock_popen: MockerFixture) -> None:
    """It returns success message."""
    mock_popen.return_value.communicate.return_value = (b"", b"")
    response = poetry.PoetryUseCase().execute(
        ["user/repo", "user/repo2"], "poetry", ("someoptionwithoutoutput",)
    )

    assert bool(response) is True
    assert response.value == "repo: poetry successful.\nrepo2: poetry successful.\n"


def test_execute_poetry_not_installed(mock_command_checker: MockerFixture) -> None:
    """It returns failure with poetry not installed message."""
    mock_command_checker.return_value = "error"
    response = poetry.PoetryUseCase().execute(
        ["user/notcloned"], "poetry", ("version",)
    )

    assert bool(response) is False
    assert "error" == response.value["message"]


def test_execute_no_folder(
    mock_command_checker: MockerFixture, mock_popen: MockerFixture
) -> None:
    """It returns error with msg file does not exist."""
    mock_command_checker.return_value = ""
    mock_exception = FileNotFoundError(2, "No such file or directory")
    mock_exception.filename = "/path/x"
    mock_popen.side_effect = mock_exception
    response = poetry.PoetryUseCase().execute(["user/x"], "poetry", ("version",))

    assert bool(response) is False
    assert response.value["message"] == "x: No such file or directory: /path/x\n"


def test_execute_error_during_execution(mock_popen: MockerFixture) -> None:
    """It returns error message."""
    mock_popen.return_value.returncode = 1
    mock_popen().communicate.return_value = (
        b"",
        b"error: pathspec 'xyz' did not match any file(s) known to poetry",
    )
    response = poetry.PoetryUseCase().execute(
        ["user/notcloned"], "poetry", ("version",)
    )

    assert bool(response) is False
    assert (
        response.value["message"]
        == "notcloned: error: pathspec 'xyz' did not match any file(s) known to poetry"
    )
