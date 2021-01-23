"""Test Github use case error handling."""
import pytest
from pytest_mock import MockerFixture

import git_portfolio.domain.config as c
import git_portfolio.use_cases.gh as gh


@pytest.fixture
def mock_config_manager(mocker: MockerFixture) -> MockerFixture:
    """Fixture for mocking CONFIG_MANAGER."""
    mock = mocker.patch("git_portfolio.config_manager.ConfigManager", autospec=True)
    mock.return_value.config = c.Config(
        "", "mytoken", ["staticdev/omg", "staticdev/omg2"]
    )
    return mock


@pytest.fixture
def mock_github_service(mocker: MockerFixture) -> MockerFixture:
    """Fixture for mocking GithubService."""
    return mocker.patch("git_portfolio.github_service.GithubService", autospec=True)


def test_call_github_service_ok(
    mocker: MockerFixture,
    mock_config_manager: MockerFixture,
    mock_github_service: MockerFixture,
) -> None:
    """It ouputs success message."""
    config_manager = mock_config_manager.return_value
    github_service = mock_github_service.return_value
    github_service.create_issue_from_repo.return_value = "success message\n"

    response = gh.GhUseCase(config_manager, github_service).call_github_service(
        "create_issue_from_repo", "", mocker.Mock(), mocker.Mock()
    )

    assert response == "success message\n"


def test_call_github_service_error(
    mocker: MockerFixture,
    mock_config_manager: MockerFixture,
    mock_github_service: MockerFixture,
) -> None:
    """It outputs error message from Github."""
    config_manager = mock_config_manager.return_value
    github_service = mock_github_service.return_value
    github_service.create_issue_from_repo.side_effect = AttributeError("some error")

    response = gh.GhUseCase(config_manager, github_service).call_github_service(
        "create_issue_from_repo", "", mocker.Mock(), mocker.Mock()
    )

    assert response == "some error"


def test_generate_response_success(
    mock_config_manager: MockerFixture, mock_github_service: MockerFixture
) -> None:
    """It returns a response success."""
    config_manager = mock_config_manager.return_value
    github_service = mock_github_service.return_value
    gh_use_case = gh.GhUseCase(config_manager, github_service)

    response = gh_use_case.generate_response("good output")

    assert bool(response) is True
    assert response.value == "good output"


def test_generate_response_failure(
    mock_config_manager: MockerFixture, mock_github_service: MockerFixture
) -> None:
    """It returns a response failure."""
    config_manager = mock_config_manager.return_value
    github_service = mock_github_service.return_value
    gh_use_case = gh.GhUseCase(config_manager, github_service)
    gh_use_case.error = True

    response = gh_use_case.generate_response("bad output")

    assert bool(response) is False
    assert response.value["message"] == "bad output"
