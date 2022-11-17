"""Test cases for the git clone use case."""
from typing import Any

import pytest
from pytest_mock import MockerFixture

import git_portfolio.responses as res
from git_portfolio.use_cases import git_clone as gcuc
from tests.conftest import ERROR_MSG
from tests.conftest import REPO
from tests.conftest import REPO2
from tests.conftest import REPO_NAME


@pytest.fixture
def mock_popen(mocker: MockerFixture) -> Any:
    """Fixture for mocking subprocess.Popen."""
    mock = mocker.patch("subprocess.Popen")
    mock.return_value.returncode = 0
    mock.return_value.communicate.return_value = (b"some output", b"")
    return mock


@pytest.fixture
def mock_github_service(mocker: MockerFixture) -> MockerFixture:
    """Fixture for mocking GithubService."""
    return mocker.patch("git_portfolio.github_service.GithubService", autospec=True)


@pytest.fixture
def mock_command_checker(mocker: MockerFixture) -> Any:
    """Fixture for mocking CommandChecker.check."""
    return mocker.patch(
        "git_portfolio.use_cases.command_checker.CommandChecker.check",
        return_value="",
    )


def test_execute_success(
    mock_github_service: MockerFixture,
    mock_command_checker: MockerFixture,
    mock_popen: MockerFixture,
) -> None:
    """It returns success messages."""
    github_service = mock_github_service.return_value
    responses = gcuc.GitCloneUseCase(github_service).execute([REPO, REPO2])

    assert len(responses) == 2
    assert isinstance(responses[0], res.ResponseSuccess)
    assert responses[0].value == f"{REPO_NAME}: clone successful.\n"


def test_execute_git_not_installed(
    mock_github_service: MockerFixture,
    mock_command_checker: MockerFixture,
) -> None:
    """It returns failure with git not installed message."""
    mock_command_checker.return_value = ERROR_MSG
    github_service = mock_github_service.return_value
    responses = gcuc.GitCloneUseCase(github_service).execute([REPO])

    mock_command_checker.assert_called_with("git")
    assert isinstance(responses[0], res.ResponseFailure)
    assert ERROR_MSG == responses[0].value["message"]


@pytest.mark.e2e
def test_execute_git_not_installed_e2e(
    mock_github_service: MockerFixture, mock_popen: MockerFixture
) -> None:
    """It returns failure with git not installed message."""
    github_service = mock_github_service.return_value
    mock_popen.side_effect = FileNotFoundError
    responses = gcuc.GitCloneUseCase(github_service).execute([REPO])

    assert isinstance(responses[0], res.ResponseFailure)
    assert (
        "This command requires git executable installed and on system path."
        == responses[0].value["message"]
    )


def test_execute_error_during_execution(
    mock_github_service: MockerFixture,
    mock_command_checker: MockerFixture,
    mock_popen: MockerFixture,
) -> None:
    """It returns error."""
    github_service = mock_github_service.return_value
    mock_popen.return_value.returncode = 1
    mock_popen().communicate.return_value = (
        b"",
        (
            f"fatal: destination path '{REPO_NAME}' already exists and is not "
            "an empty directory.\n"
        ).encode(),
    )
    responses = gcuc.GitCloneUseCase(github_service).execute([REPO])

    assert isinstance(responses[0], res.ResponseFailure)
    assert responses[0].value["message"] == (
        f"{REPO_NAME}: fatal: destination path '{REPO_NAME}' already exists and is not "
        "an empty directory.\n"
    )
