"""Test cases for the Github create PR use case."""
from typing import List

import pytest
from pytest_mock import MockerFixture

import git_portfolio.domain.config as c
import git_portfolio.domain.pull_request as pr
import git_portfolio.use_cases.gh_create_pr_use_case as ghcp


@pytest.fixture
def mock_github_manager(mocker: MockerFixture) -> MockerFixture:
    """Fixture for mocking GithubManager."""
    mock = mocker.patch("git_portfolio.github_manager.GithubManager", autospec=True)
    mock.return_value.config = c.Config(
        "", "mytoken", ["staticdev/omg", "staticdev/omg2"]
    )
    mock.return_value.create_pull_request_from_repo.return_value = "success message\n"
    return mock


@pytest.fixture
def domain_prs() -> List[pr.PullRequest]:
    """Pull requests fixture."""
    prs = [
        pr.PullRequest(
            "my title",
            "my body",
            {"testing"},
            False,
            "",
            False,
            "main",
            "branch",
            True,
        ),
        pr.PullRequest(
            "my title",
            "my body",
            set(),
            True,
            "issue title",
            True,
            "main",
            "branch",
            True,
        ),
    ]
    return prs


def test_execute_for_all_repos(
    mock_github_manager: MockerFixture, domain_prs: List[pr.PullRequest]
) -> None:
    """It returns success."""
    github_manager = mock_github_manager.return_value
    request = domain_prs[0]
    response = ghcp.GhCreatePrUseCase(github_manager).execute(request)

    assert bool(response) is True
    assert "success message\nsuccess message\n" == response.value


def test_execute_link_issue(
    mock_github_manager: MockerFixture, domain_prs: List[pr.PullRequest]
) -> None:
    """It returns success."""
    github_manager = mock_github_manager.return_value
    request = domain_prs[1]
    response = ghcp.GhCreatePrUseCase(github_manager).execute(request)

    assert bool(response) is True
    assert "success message\nsuccess message\n" == response.value


def test_execute_for_specific_repo(
    mock_github_manager: MockerFixture, domain_prs: List[pr.PullRequest]
) -> None:
    """It returns success."""
    github_manager = mock_github_manager.return_value
    request = domain_prs[0]
    response = ghcp.GhCreatePrUseCase(github_manager).execute(request, "staticdev/omg")

    assert bool(response) is True
    assert "success message\n" == response.value


def test_execute_link_issue_for_specific_repo(
    mock_github_manager: MockerFixture, domain_prs: List[pr.PullRequest]
) -> None:
    """It returns success."""
    github_manager = mock_github_manager.return_value
    request = domain_prs[1]
    response = ghcp.GhCreatePrUseCase(github_manager).execute(request, "staticdev/omg")

    assert bool(response) is True
    assert "success message\n" == response.value
