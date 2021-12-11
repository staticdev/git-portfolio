"""Test cases for git use case."""
import pytest
from pytest_mock import MockerFixture
from tests.conftest import REPO
from tests.conftest import REPO2
from tests.conftest import REPO_NAME

import git_portfolio.responses as res
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
    responses = git.GitUseCase().execute([REPO, REPO2], "checkout", ("xx",))

    assert len(responses) == 2
    assert isinstance(responses[0], res.ResponseSuccess)
    assert responses[0].value == f"{REPO_NAME}: some output"


def test_execute_success_no_output(mock_popen: MockerFixture) -> None:
    """It returns success message."""
    mock_popen.return_value.communicate.return_value = (b"", b"")
    # case where command success has no output with `add .`
    responses = git.GitUseCase().execute([REPO, REPO2], "add", (".",))

    assert len(responses) == 2
    assert isinstance(responses[0], res.ResponseSuccess)
    assert responses[0].value == f"{REPO_NAME}: add successful.\n"


def test_execute_git_not_installed(mock_command_checker: MockerFixture) -> None:
    """It returns failure with git not installed message."""
    mock_command_checker.return_value = "error"
    responses = git.GitUseCase().execute([REPO], "checkout", ("xx",))

    assert isinstance(responses[0], res.ResponseFailure)
    assert "error" == responses[0].value["message"]


def test_execute_no_folder(
    mock_command_checker: MockerFixture, mock_popen: MockerFixture
) -> None:
    """It returns error with msg file does not exist."""
    mock_command_checker.return_value = ""
    mock_exception = FileNotFoundError(2, "No such file or directory")
    mock_exception.filename = f"/path/{REPO_NAME}"
    mock_popen.side_effect = mock_exception
    responses = git.GitUseCase().execute([REPO], "checkout", ("xx",))

    assert isinstance(responses[0], res.ResponseFailure)
    assert (
        responses[0].value["message"]
        == f"{REPO_NAME}: No such file or directory: /path/{REPO_NAME}\n"
    )


def test_execute_error_during_execution(mock_popen: MockerFixture) -> None:
    """It returns error message."""
    mock_popen.return_value.returncode = 1
    mock_popen().communicate.return_value = (
        b"",
        b"fatal: A branch named 'existingbranch' already exists.",
    )
    # case where create branch already exists with `checkout -b existingbranch`
    responses = git.GitUseCase().execute([REPO], "checkout", ("-b", "existingbranch"))

    assert isinstance(responses[0], res.ResponseFailure)
    assert (
        responses[0].value["message"]
        == f"{REPO_NAME}: fatal: A branch named 'existingbranch' already exists."
    )


def test_execute_error_no_stderr(mock_popen: MockerFixture) -> None:
    """It returns success message with the stdout on output."""
    mock_popen.return_value.returncode = 1
    mock_popen().communicate.return_value = (
        (
            b"On branch main\nYour branch is up to date with 'origin/main'.\n\n"
            b"nothing to commit, working tree clean"
        ),
        b"",
    )
    # case where is nothing to commit with `commit`
    responses = git.GitUseCase().execute([REPO], "commit", ("",))

    assert isinstance(responses[0], res.ResponseSuccess)
    assert responses[0].value == (
        f"{REPO_NAME}: On branch main\nYour branch is up to date with 'origin/main'."
        "\n\nnothing to commit, working tree clean\n"
    )
