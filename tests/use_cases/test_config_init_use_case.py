"""Test cases for the gitp config initialization use case."""
import pytest
from pytest_mock import MockerFixture

import git_portfolio.domain.gh_connection_settings as cs
import git_portfolio.response_objects as res
import git_portfolio.use_cases.config_init_use_case as ci


@pytest.fixture
def mock_config_manager(mocker: MockerFixture) -> MockerFixture:
    """Fixture for mocking ConfigManager."""
    return mocker.patch("git_portfolio.config_manager.ConfigManager", autospec=True)


@pytest.fixture
def mock_github_service(mocker: MockerFixture) -> MockerFixture:
    """Fixture for mocking GithubService."""
    return mocker.patch("git_portfolio.github_service.GithubService", autospec=True)


@pytest.fixture
def mock_prompt_inquirer_prompter(mocker: MockerFixture) -> MockerFixture:
    """Fixture for mocking prompt.InquirerPrompter."""
    return mocker.patch("git_portfolio.prompt.InquirerPrompter", autospec=True)


@pytest.fixture
def mock_config_repos_use_case(mocker: MockerFixture) -> MockerFixture:
    """Fixture for mocking ConfigReposUseCase."""
    return mocker.patch(
        "git_portfolio.use_cases.config_repos_use_case.ConfigReposUseCase",
        autospec=True,
    )


@pytest.fixture
def domain_gh_conn_settings() -> cs.GhConnectionSettings:
    """Issue fixture."""
    gh_conn_settings = cs.GhConnectionSettings(
        "mytoken",
        "myhost.com",
    )
    return gh_conn_settings


def test_execute_success(
    mock_config_manager: MockerFixture,
    mock_github_service: MockerFixture,
    mock_prompt_inquirer_prompter: MockerFixture,
    domain_gh_conn_settings: cs.GhConnectionSettings,
    mock_config_repos_use_case: MockerFixture,
) -> None:
    """It returns success."""
    config_manager = mock_config_manager.return_value
    response = ci.ConfigInitUseCase(config_manager).execute(domain_gh_conn_settings)

    assert bool(response) is True
    assert "gitp successfully configured." == response.value


def test_execute_attribute_error(
    mock_config_manager: MockerFixture,
    mock_github_service: MockerFixture,
    mock_prompt_inquirer_prompter: MockerFixture,
    domain_gh_conn_settings: cs.GhConnectionSettings,
    mock_config_repos_use_case: MockerFixture,
) -> None:
    """It returns success."""
    config_manager = mock_config_manager.return_value
    mock_github_service.side_effect = AttributeError
    response = ci.ConfigInitUseCase(config_manager).execute(domain_gh_conn_settings)

    assert bool(response) is False
    assert response.type == res.ResponseFailure.PARAMETERS_ERROR


def test_execute_connection_error(
    mock_config_manager: MockerFixture,
    mock_github_service: MockerFixture,
    mock_prompt_inquirer_prompter: MockerFixture,
    domain_gh_conn_settings: cs.GhConnectionSettings,
    mock_config_repos_use_case: MockerFixture,
) -> None:
    """It returns success."""
    config_manager = mock_config_manager.return_value
    mock_github_service.side_effect = ConnectionError
    response = ci.ConfigInitUseCase(config_manager).execute(domain_gh_conn_settings)

    assert bool(response) is False
    assert response.type == res.ResponseFailure.SYSTEM_ERROR
