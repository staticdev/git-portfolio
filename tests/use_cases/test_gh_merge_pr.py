"""Test cases for the Github merge PR use case."""
from typing import List

import pytest
from pytest_mock import MockerFixture

import git_portfolio.domain.config as c
import git_portfolio.domain.pull_request_merge as mpr
import git_portfolio.use_cases.gh_merge_pr as ghmp


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
    mock = mocker.patch("git_portfolio.github_service.GithubService", autospec=True)
    mock.return_value.merge_pull_request_from_repo.return_value = "success message\n"
    return mock


@pytest.fixture
def mock_gh_delete_branch_use_case(mocker: MockerFixture) -> MockerFixture:
    """Fixture for mocking GhDeleteBranchUseCase."""
    return mocker.patch(
        "git_portfolio.use_cases.gh_delete_branch.GhDeleteBranchUseCase",
        autospec=True,
    )


@pytest.fixture
def domain_mprs() -> List[mpr.PullRequestMerge]:
    """Pull request merge fixture."""
    mprs = [
        mpr.PullRequestMerge("branch", "main", "org name", False),
        mpr.PullRequestMerge("branch-2", "main", "org name", True),
    ]
    return mprs


def test_execute_for_all_repos(
    mock_config_manager: MockerFixture,
    mock_github_service: MockerFixture,
    domain_mprs: List[mpr.PullRequestMerge],
) -> None:
    """It returns success."""
    config_manager = mock_config_manager.return_value
    github_service = mock_github_service.return_value
    response = ghmp.GhMergePrUseCase(config_manager, github_service).execute(
        domain_mprs[0]
    )

    assert bool(response) is True
    assert "success message\nsuccess message\n" == response.value


def test_execute_delete_branch(
    mock_config_manager: MockerFixture,
    mock_github_service: MockerFixture,
    mock_gh_delete_branch_use_case: MockerFixture,
    domain_mprs: List[mpr.PullRequestMerge],
) -> None:
    """It returns success."""
    config_manager = mock_config_manager.return_value
    github_service = mock_github_service.return_value
    response = ghmp.GhMergePrUseCase(config_manager, github_service).execute(
        domain_mprs[1]
    )

    assert bool(response) is True
    assert "success message\nsuccess message\n" == response.value
    mock_gh_delete_branch_use_case.assert_called()


def test_execute_for_specific_repo(
    mock_config_manager: MockerFixture,
    mock_github_service: MockerFixture,
    domain_mprs: List[mpr.PullRequestMerge],
) -> None:
    """It returns success."""
    config_manager = mock_config_manager.return_value
    github_service = mock_github_service.return_value
    response = ghmp.GhMergePrUseCase(config_manager, github_service).execute(
        domain_mprs[0], REPO
    )
    assert bool(response) is True
    assert "success message\n" == response.value


def test_execute_delete_branch_for_specific_repo(
    mock_config_manager: MockerFixture,
    mock_github_service: MockerFixture,
    mock_gh_delete_branch_use_case: MockerFixture,
    domain_mprs: List[mpr.PullRequestMerge],
) -> None:
    """It returns success."""
    config_manager = mock_config_manager.return_value
    github_service = mock_github_service.return_value
    response = ghmp.GhMergePrUseCase(config_manager, github_service).execute(
        domain_mprs[1], REPO
    )

    assert bool(response) is True
    assert "success message\n" == response.value
    mock_gh_delete_branch_use_case.assert_called_once()
