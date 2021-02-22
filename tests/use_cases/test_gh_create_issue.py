"""Test cases for the Github create issue use case."""
import pytest
from pytest_mock import MockerFixture

import git_portfolio.domain.config as c
import git_portfolio.domain.issue as i
import git_portfolio.use_cases.gh_create_issue as ghci


REPO = "org/repo-name"
REPO2 = "org/repo-name2"


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


def test_action(
    mock_config_manager: MockerFixture,
    mock_github_service: MockerFixture,
    domain_issue: i.Issue,
) -> None:
    """It returns success."""
    config_manager = mock_config_manager.return_value
    github_service = mock_github_service.return_value
    use_case = ghci.GhCreateIssueUseCase(config_manager, github_service)
    use_case.action(REPO, domain_issue)

    assert "success message\n" == use_case.output
