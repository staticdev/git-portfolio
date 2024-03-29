"""Test Github use case error handling."""
from __future__ import annotations

import pytest
from pytest_mock import MockerFixture

import git_portfolio.domain.config as c
import git_portfolio.responses as res
import git_portfolio.use_cases.gh as gh
from tests.conftest import ERROR_MSG
from tests.conftest import REPO
from tests.conftest import REPO2
from tests.conftest import SUCCESS_MSG
from tests.test_github_service import FakeGithubService


class FakeGhUseCase(gh.GhUseCase):
    """Github fake use case."""

    def action(self, github_repo: str) -> None:  # type: ignore[override]
        """Fake action."""
        self.call_github_service("fake_success", github_repo)


@pytest.fixture
def mock_config_manager(mocker: MockerFixture) -> MockerFixture:
    """Fixture for mocking CONFIG_MANAGER."""
    mock = mocker.patch("git_portfolio.config_manager.ConfigManager", autospec=True)
    mock.return_value.config = c.Config("", "my-token", [REPO, REPO2])
    return mock


def test_call_github_service_ok(
    mock_config_manager: MockerFixture,
) -> None:
    """It ouputs success message."""
    config_manager = mock_config_manager.return_value
    gh_use_case = FakeGhUseCase(config_manager, FakeGithubService())

    response = gh_use_case.call_github_service("fake_success", REPO)

    assert isinstance(response, res.ResponseSuccess)
    assert response.value == SUCCESS_MSG


def test_call_github_service_error(
    mock_config_manager: MockerFixture,
) -> None:
    """It outputs error message from Github."""
    config_manager = mock_config_manager.return_value
    gh_use_case = FakeGhUseCase(config_manager, FakeGithubService())

    response = gh_use_case.call_github_service("fake_error", REPO)

    assert isinstance(response, res.ResponseFailure)
    assert response.value["message"] == ERROR_MSG


def test_call_github_service_unexpected_error(
    mock_config_manager: MockerFixture,
) -> None:
    """It outputs instructions for issue creation."""
    config_manager = mock_config_manager.return_value
    gh_use_case = FakeGhUseCase(config_manager, FakeGithubService())

    response = gh_use_case.call_github_service("fake_unexpected_error", REPO)

    assert isinstance(response, res.ResponseFailure)
    assert isinstance(response.value["message"], str)
    assert response.value["message"].startswith(
        "An unexpected error occured. Please report at "
    )
    assert response.value["message"].endswith(f"{ERROR_MSG}\n")


def test_execute_for_all_repos(
    mock_config_manager: MockerFixture,
) -> None:
    """It returns success."""
    config_manager = mock_config_manager.return_value
    gh_use_case = FakeGhUseCase(config_manager, FakeGithubService())

    responses = gh_use_case.execute()

    assert len(responses) == 2
    for response in responses:
        assert bool(response) is True


def test_execute_for_specific_repo(
    mock_config_manager: MockerFixture,
) -> None:
    """It returns success."""
    config_manager = mock_config_manager.return_value
    gh_use_case = FakeGhUseCase(config_manager, FakeGithubService(), REPO)

    responses = gh_use_case.execute()

    assert len(responses) == 1
    assert bool(responses[0]) is True
