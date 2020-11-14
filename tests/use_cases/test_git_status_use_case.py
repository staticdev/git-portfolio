"""Test cases for the git status use case."""
from typing import Any

import pytest
from pytest_mock import MockerFixture

from git_portfolio.use_cases import git_status_use_case as gsus


@pytest.fixture
def mock_git_usecase(mocker: MockerFixture) -> MockerFixture:
    """Fixture for mocking GitUseCase."""
    mock = mocker.patch(
        "git_portfolio.use_cases.git_use_case.GitUseCase", autospec=True
    )
    mock.check_git_install.return_value = ""
    return mock


@pytest.fixture
def mock_popen(mocker: MockerFixture) -> Any:
    """Fixture for mocking subprocess.Popen."""
    mock = mocker.patch("subprocess.Popen")
    mock.return_value.returncode = 0
    mock.return_value.communicate.return_value = (b"some output", b"")
    return mock


@pytest.mark.e2e
def test_execute_git_not_installed(mock_popen: MockerFixture) -> None:
    """It returns failure with git not installed message."""
    mock_popen.side_effect = FileNotFoundError
    response = gsus.GitStatusUseCase().execute(["staticdev/omg"], ("",))

    assert bool(response) is False
    assert (
        "This command requires Git executable installed and on system path."
        == response.value["message"]
    )


def test_execute_success(
    mock_git_usecase: MockerFixture, mock_popen: MockerFixture
) -> None:
    """It returns success messages."""
    response = gsus.GitStatusUseCase().execute(
        ["staticdev/omg", "staticdev/omg2"], ("",)
    )

    assert bool(response) is True
    assert response.value == "omg: some output\nomg2: some output\n"


def test_execute_error_during_execution(
    mock_git_usecase: MockerFixture, mock_popen: MockerFixture
) -> None:
    """It returns success message with the error on output."""
    mock_exception = FileNotFoundError(2, "No such file or directory")
    mock_exception.filename = "/path/x"
    mock_popen.side_effect = mock_exception
    response = gsus.GitStatusUseCase().execute(["staticdev/x"], ("",))

    assert bool(response) is True
    assert response.value == ("x: No such file or directory: /path/x\n")
