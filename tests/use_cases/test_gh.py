"""Test Github use case error handling."""
import pytest
from pytest_mock import MockerFixture

import git_portfolio.domain.config as c
import git_portfolio.use_cases.gh as gh


REPO = "org/reponame"
REPO2 = "org/reponame2"


@pytest.fixture
def mock_config_manager(mocker: MockerFixture) -> MockerFixture:
    """Fixture for mocking CONFIG_MANAGER."""
    mock = mocker.patch("git_portfolio.config_manager.ConfigManager", autospec=True)
    mock.return_value.config = c.Config("", "mytoken", [REPO, REPO2])
    return mock


@pytest.fixture
def mock_github_service(mocker: MockerFixture) -> MockerFixture:
    """Fixture for mocking GithubService."""
    return mocker.patch("git_portfolio.github_service.GithubService", autospec=True)


@pytest.fixture
def mock_action(mocker: MockerFixture) -> MockerFixture:
    """Fixture for mocking GhUseCase.action."""
    return mocker.patch("git_portfolio.use_cases.gh.GhUseCase.action")


def test_call_github_service_ok(
    mocker: MockerFixture,
    mock_config_manager: MockerFixture,
    mock_github_service: MockerFixture,
) -> None:
    """It ouputs success message."""
    config_manager = mock_config_manager.return_value
    github_service = mock_github_service.return_value
    github_service.create_issue_from_repo.return_value = "success message\n"
    gh_use_case = gh.GhUseCase(config_manager, github_service)

    gh_use_case.call_github_service(
        "create_issue_from_repo", mocker.Mock(), mocker.Mock()
    )

    assert gh_use_case.output == "success message\n"


def test_call_github_service_error(
    mocker: MockerFixture,
    mock_config_manager: MockerFixture,
    mock_github_service: MockerFixture,
) -> None:
    """It outputs error message from Github."""
    config_manager = mock_config_manager.return_value
    github_service = mock_github_service.return_value
    github_service.create_issue_from_repo.side_effect = AttributeError("some error")
    gh_use_case = gh.GhUseCase(config_manager, github_service)

    gh_use_case.call_github_service(
        "create_issue_from_repo", mocker.Mock(), mocker.Mock()
    )

    assert gh_use_case.output == "some error"


def test_generate_response_success(
    mock_config_manager: MockerFixture, mock_github_service: MockerFixture
) -> None:
    """It returns a response success."""
    config_manager = mock_config_manager.return_value
    github_service = mock_github_service.return_value
    gh_use_case = gh.GhUseCase(config_manager, github_service)
    gh_use_case.error = False
    gh_use_case.output = "good output"

    response = gh_use_case.generate_response()

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
    gh_use_case.output = "bad output"

    response = gh_use_case.generate_response()

    assert bool(response) is False
    assert response.value["message"] == "bad output"


def test_execute_for_all_repos(
    mock_config_manager: MockerFixture,
    mock_github_service: MockerFixture,
    mock_action: MockerFixture,
) -> None:
    """It returns success."""
    config_manager = mock_config_manager.return_value
    github_service = mock_github_service.return_value
    gh_use_case = gh.GhUseCase(config_manager, github_service)

    response = gh_use_case.execute()

    assert mock_action.call_count == 2
    assert bool(response) is True


def test_execute_for_specific_repo(
    mock_config_manager: MockerFixture,
    mock_github_service: MockerFixture,
    mock_action: MockerFixture,
) -> None:
    """It returns success."""
    config_manager = mock_config_manager.return_value
    github_service = mock_github_service.return_value
    gh_use_case = gh.GhUseCase(config_manager, github_service, REPO)

    response = gh_use_case.execute()

    assert mock_action.call_count == 1
    assert bool(response) is True
