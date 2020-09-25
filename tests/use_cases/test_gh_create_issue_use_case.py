"""Test cases for the Github create issue use case."""
from unittest.mock import Mock

import pytest
from pytest_mock import MockerFixture

import git_portfolio.domain.config as c
import git_portfolio.domain.issue as i
import git_portfolio.use_cases.gh_create_issue_use_case as ghci


@pytest.fixture
def mock_github_manager(mocker: MockerFixture) -> MockerFixture:
    """Fixture for mocking GithubManager."""
    mock = mocker.patch("git_portfolio.github_manager.GithubManager", autospec=True)
    mock.return_value.config = c.Config("", "mytoken", ["staticdev/omg"])
    mock.return_value.github_connection = Mock()
    return mock


@pytest.fixture
def domain_issue() -> i.Issue:
    """Issue fixture."""
    issue = i.Issue(
        "my title",
        "my body",
        "testing,refactor",
    )
    return issue


def test_execute_for_all_repos(
    mock_github_manager: MockerFixture, domain_issue: i.Issue
) -> None:
    """It returns success."""
    github_manager = mock_github_manager.return_value
    response = ghci.GhCreateIssueUseCase(github_manager).execute(domain_issue)

    assert bool(response) is True
    assert "staticdev/omg: issue created successfully." == response.value


def test_execute_for_specific_repo(
    mock_github_manager: MockerFixture, domain_issue: i.Issue
) -> None:
    """It returns success."""
    github_manager = mock_github_manager.return_value
    response = ghci.GhCreateIssueUseCase(github_manager).execute(
        domain_issue, "staticdev/omg"
    )

    assert bool(response) is True
    assert "staticdev/omg: issue created successfully." == response.value