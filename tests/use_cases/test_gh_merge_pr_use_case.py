"""Test cases for the Github merge PR use case."""
from typing import List

import pytest
from pytest_mock import MockerFixture

import git_portfolio.domain.config as c
import git_portfolio.domain.pull_request_merge as mpr
import git_portfolio.use_cases.gh_merge_pr_use_case as ghmp


@pytest.fixture
def mock_github_manager(mocker: MockerFixture) -> MockerFixture:
    """Fixture for mocking GithubManager."""
    mock = mocker.patch("git_portfolio.github_manager.GithubManager", autospec=True)
    mock.return_value.config = c.Config(
        "", "mytoken", ["staticdev/omg", "staticdev/omg2"]
    )
    mock.return_value.merge_pull_request_from_repo.return_value = "success message\n"
    return mock


@pytest.fixture
def mock_gh_delete_branch_use_case(mocker: MockerFixture) -> MockerFixture:
    """Fixture for mocking GhDeleteBranchUseCase."""
    return mocker.patch(
        "git_portfolio.use_cases.gh_delete_branch_use_case.GhDeleteBranchUseCase",
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
    mock_github_manager: MockerFixture, domain_mprs: List[mpr.PullRequestMerge]
) -> None:
    """It returns success."""
    github_manager = mock_github_manager.return_value
    response = ghmp.GhMergePrUseCase(github_manager).execute(domain_mprs[0])

    assert bool(response) is True
    assert "success message\nsuccess message\n" == response.value


def test_execute_delete_branch(
    mock_github_manager: MockerFixture,
    mock_gh_delete_branch_use_case: MockerFixture,
    domain_mprs: List[mpr.PullRequestMerge],
) -> None:
    """It returns success."""
    github_manager = mock_github_manager.return_value
    response = ghmp.GhMergePrUseCase(github_manager).execute(domain_mprs[1])

    assert bool(response) is True
    assert "success message\nsuccess message\n" == response.value
    mock_gh_delete_branch_use_case.assert_called()


def test_execute_for_specific_repo(
    mock_github_manager: MockerFixture, domain_mprs: List[mpr.PullRequestMerge]
) -> None:
    """It returns success."""
    github_manager = mock_github_manager.return_value
    response = ghmp.GhMergePrUseCase(github_manager).execute(
        domain_mprs[0], "staticdev/omg"
    )
    assert bool(response) is True
    assert "success message\n" == response.value


def test_execute_delete_branch_for_specific_repo(
    mock_github_manager: MockerFixture,
    mock_gh_delete_branch_use_case: MockerFixture,
    domain_mprs: List[mpr.PullRequestMerge],
) -> None:
    """It returns success."""
    github_manager = mock_github_manager.return_value
    response = ghmp.GhMergePrUseCase(github_manager).execute(
        domain_mprs[1], "staticdev/omg"
    )

    assert bool(response) is True
    assert "success message\n" == response.value
    mock_gh_delete_branch_use_case.assert_called_once()
