"""Test cases for the Github create PR use case."""
from typing import List

import pytest
from pytest_mock import MockerFixture

import git_portfolio.domain.config as c
import git_portfolio.domain.pull_request as pr
import git_portfolio.use_cases.gh_create_pr_use_case as ghcp


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
    mock_config_manager: MockerFixture,
    mock_github_service: MockerFixture,
    domain_prs: List[pr.PullRequest],
) -> None:
    """It returns success."""
    config_manager = mock_config_manager.return_value
    github_service = mock_github_service.return_value
    request = domain_prs[0]
    response = ghcp.GhCreatePrUseCase(config_manager, github_service).execute(request)

    assert bool(response) is True
    assert "success message\nsuccess message\n" == response.value


def test_execute_link_issue(
    mock_config_manager: MockerFixture,
    mock_github_service: MockerFixture,
    domain_prs: List[pr.PullRequest],
) -> None:
    """It returns success."""
    config_manager = mock_config_manager.return_value
    github_service = mock_github_service.return_value
    request = domain_prs[1]
    response = ghcp.GhCreatePrUseCase(config_manager, github_service).execute(request)

    assert bool(response) is True
    assert "success message\nsuccess message\n" == response.value


def test_execute_for_specific_repo(
    mock_config_manager: MockerFixture,
    mock_github_service: MockerFixture,
    domain_prs: List[pr.PullRequest],
) -> None:
    """It returns success."""
    config_manager = mock_config_manager.return_value
    github_service = mock_github_service.return_value
    request = domain_prs[0]
    response = ghcp.GhCreatePrUseCase(config_manager, github_service).execute(
        request, "staticdev/omg"
    )

    assert bool(response) is True
    assert "success message\n" == response.value


def test_execute_link_issue_for_specific_repo(
    mock_config_manager: MockerFixture,
    mock_github_service: MockerFixture,
    domain_prs: List[pr.PullRequest],
) -> None:
    """It returns success."""
    config_manager = mock_config_manager.return_value
    github_service = mock_github_service.return_value
    request = domain_prs[1]
    response = ghcp.GhCreatePrUseCase(config_manager, github_service).execute(
        request, "staticdev/omg"
    )

    assert bool(response) is True
    assert "success message\n" == response.value
