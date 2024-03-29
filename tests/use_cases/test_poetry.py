"""Test cases for poetry use case."""
import pytest
from pytest_mock import MockerFixture

import git_portfolio.responses as res
import git_portfolio.use_cases.poetry as poetry
from tests.conftest import REPO
from tests.conftest import REPO2
from tests.conftest import REPO_NAME


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

    responses = poetry.PoetryUseCase().execute([REPO, REPO2], "poetry", ("version",))

    assert len(responses) == 2
    assert isinstance(responses[0], res.ResponseSuccess)
    assert responses[0].value == f"{REPO_NAME}: some output"


def test_execute_poetry_not_installed(mock_command_checker: MockerFixture) -> None:
    """It returns failure with poetry not installed message."""
    mock_command_checker.return_value = "error"

    responses = poetry.PoetryUseCase().execute([REPO], "poetry", ("version",))

    assert isinstance(responses[0], res.ResponseFailure)
    assert "error" == responses[0].value["message"]


def test_execute_no_folder(
    mock_command_checker: MockerFixture, mock_popen: MockerFixture
) -> None:
    """It returns error with msg file does not exist."""
    mock_command_checker.return_value = ""
    mock_exception = FileNotFoundError(2, "No such file or directory")
    mock_exception.filename = "/path/x"
    mock_popen.side_effect = mock_exception

    responses = poetry.PoetryUseCase().execute([REPO], "poetry", ("version",))

    assert isinstance(responses[0], res.ResponseFailure)
    assert (
        responses[0].value["message"]
        == f"{REPO_NAME}: No such file or directory: /path/x\n"
    )


def test_execute_error_during_execution(mock_popen: MockerFixture) -> None:
    """It returns error message."""
    mock_popen.return_value.returncode = 1
    mock_popen().communicate.return_value = (
        b"ValueError\n\nPackage nonexistingpackage not found",
        b"",
    )
    responses = poetry.PoetryUseCase().execute(
        [REPO], "poetry", ("remove", "nonexistingpackage")
    )

    assert isinstance(responses[0], res.ResponseFailure)
    assert responses[0].value["message"] == (
        f"{REPO_NAME}: ValueError\n\nPackage nonexistingpackage not found"
    )
