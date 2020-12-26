"""Test cases for the Github create issue use case."""
import pytest
from pytest_mock import MockerFixture

import git_portfolio.domain.config as c
import git_portfolio.domain.issue as i
import git_portfolio.use_cases.gh_create_issue as ghci


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
    mock = mocker.patch("git_portfolio.github_service.GithubService", autospec=True)
    mock.return_value.create_issue_from_repo.return_value = "success message\n"
    return mock


@pytest.fixture
def domain_issue() -> i.Issue:
    """Issue fixture."""
    issue = i.Issue(
        0,
        "my title",
        "my body",
        {"testing", "refactor"},
    )
    return issue


def test_execute_for_all_repos(
    mock_config_manager: MockerFixture,
    mock_github_service: MockerFixture,
    domain_issue: i.Issue,
) -> None:
    """It returns success."""
    config_manager = mock_config_manager.return_value
    github_service = mock_github_service.return_value
    response = ghci.GhCreateIssueUseCase(config_manager, github_service).execute(
        domain_issue
    )

    assert bool(response) is True
    assert "success message\nsuccess message\n" == response.value


def test_execute_for_specific_repo(
    mock_config_manager: MockerFixture,
    mock_github_service: MockerFixture,
    domain_issue: i.Issue,
) -> None:
    """It returns success."""
    config_manager = mock_config_manager.return_value
    github_service = mock_github_service.return_value
    response = ghci.GhCreateIssueUseCase(config_manager, github_service).execute(
        domain_issue, "staticdev/omg"
    )

    assert bool(response) is True
    assert "success message\n" == response.value
