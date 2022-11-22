"""Test cases for the Github create issue use case."""
import pytest
from pytest_mock import MockerFixture

import git_portfolio.domain.config as c
import git_portfolio.responses as res
import git_portfolio.use_cases.gh_create_issue as ghci
from tests.conftest import DOMAIN_ISSUES
from tests.conftest import REPO
from tests.conftest import SUCCESS_MSG


@pytest.fixture
def mock_config_manager(mocker: MockerFixture) -> MockerFixture:
    """Fixture for mocking CONFIG_MANAGER."""
    mock = mocker.patch("git_portfolio.config_manager.ConfigManager", autospec=True)
    mock.return_value.config = c.Config("", "my-token", [REPO])
    return mock


@pytest.fixture
def mock_github_service(mocker: MockerFixture) -> MockerFixture:
    """Fixture for mocking GithubService."""
    mock = mocker.patch("git_portfolio.github_service.GithubService", autospec=True)
    mock.return_value.create_issue_from_repo.return_value = SUCCESS_MSG
    return mock


def test_action(
    mock_config_manager: MockerFixture,
    mock_github_service: MockerFixture,
) -> None:
    """It returns success."""
    config_manager = mock_config_manager.return_value
    github_service = mock_github_service.return_value
    use_case = ghci.GhCreateIssueUseCase(config_manager, github_service)

    use_case.action(REPO, DOMAIN_ISSUES[0])
    response = use_case.responses[0]

    assert isinstance(response, res.ResponseSuccess)
    assert SUCCESS_MSG == response.value
