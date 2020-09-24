"""Test cases for the gitp config initialization use case."""
import pytest
from pytest_mock import MockerFixture

import git_portfolio.use_cases.config_init_use_case as ci


@pytest.fixture
def mock_config_manager(mocker: MockerFixture) -> MockerFixture:
    """Fixture for mocking ConfigManager."""
    return mocker.patch("git_portfolio.config_manager.ConfigManager", autospec=True)


@pytest.fixture
def mock_github_manager(mocker: MockerFixture) -> MockerFixture:
    """Fixture for mocking GithubManager."""
    return mocker.patch("git_portfolio.github_manager.GithubManager", autospec=True)


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


def test_execute(
    mock_config_manager: MockerFixture,
    mock_github_manager: MockerFixture,
    mock_prompt_inquirer_prompter: MockerFixture,
    mock_config_repos_use_case: MockerFixture,
) -> None:
    """It returns success."""
    config_manager = mock_config_manager.return_value
    github_manager = mock_github_manager.return_value
    response = ci.ConfigInitUseCase(config_manager, github_manager).execute()

    assert bool(response) is True
    assert "gitp successfully configured." == response.value
