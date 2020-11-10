"""Test cases for the git clone use case."""
from typing import Any

import pytest
from pytest_mock import MockerFixture

from git_portfolio.use_cases import git_clone_use_case as gcuc


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


def test_execute_git_not_installed(
    mock_github_service: MockerFixture, mock_popen: MockerFixture
) -> None:
    """It returns failure with git not installed message."""
    github_service = mock_github_service.return_value
    mock_popen.side_effect = FileNotFoundError
    response = gcuc.GitCloneUseCase(github_service).execute(["staticdev/notcloned"])

    assert bool(response) is False
    assert (
        "This command requires Git executable installed and on system path."
        == response.value["message"]
    )


def test_execute_success(
    mock_github_service: MockerFixture, mock_popen: MockerFixture
) -> None:
    """It returns success messages."""
    github_service = mock_github_service.return_value
    response = gcuc.GitCloneUseCase(github_service).execute(
        ["staticdev/omg", "staticdev/omg2"]
    )

    assert bool(response) is True
    assert response.value == "omg: clone successful.\nomg2: clone successful.\n"


def test_execute_error_during_execution(
    mock_github_service: MockerFixture, mock_popen: MockerFixture
) -> None:
    """It returns success message with the error on output."""
    github_service = mock_github_service.return_value
    mock_popen.return_value.returncode = 1
    mock_popen().communicate.return_value = (
        b"",
        b"fatal: destination path 'x' already exists and is not an empty directory.\n",
    )
    response = gcuc.GitCloneUseCase(github_service).execute(["staticdev/x"])

    assert bool(response) is True
    assert response.value == (
        "x: fatal: destination path 'x' already exists and is not an empty "
        "directory.\n"
    )
