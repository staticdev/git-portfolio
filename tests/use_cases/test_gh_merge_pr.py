"""Test cases for the Github merge PR use case."""
from __future__ import annotations

import pytest
from pytest_mock import MockerFixture

import git_portfolio.domain.config as c
import git_portfolio.domain.pull_request_merge as mpr
import git_portfolio.use_cases.gh_merge_pr as ghmp


REPO = "org/repo-name"


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
def domain_mprs() -> list[mpr.PullRequestMerge]:
    """Pull request merge fixture."""
    mprs = [
        mpr.PullRequestMerge("branch", "main", "org name", False),
        mpr.PullRequestMerge("branch-2", "main", "org name", True),
    ]
    return mprs


def test_action(
    mock_config_manager: MockerFixture,
    mock_github_service: MockerFixture,
    domain_mprs: list[mpr.PullRequestMerge],
) -> None:
    """It returns success."""
    config_manager = mock_config_manager.return_value
    github_service = mock_github_service.return_value
    use_case = ghmp.GhMergePrUseCase(config_manager, github_service)
    use_case.action(REPO, domain_mprs[0])

    assert "success message\n" == use_case.output


def test_action_delete_branch(
    mock_config_manager: MockerFixture,
    mock_github_service: MockerFixture,
    mock_gh_delete_branch_use_case: MockerFixture,
    domain_mprs: list[mpr.PullRequestMerge],
) -> None:
    """It returns success."""
    config_manager = mock_config_manager.return_value
    github_service = mock_github_service.return_value
    use_case = ghmp.GhMergePrUseCase(config_manager, github_service)
    use_case.action(REPO, domain_mprs[1])

    assert "success message\n" == use_case.output
    mock_gh_delete_branch_use_case.assert_called_once()


@pytest.mark.integration
def test_action_delete_branch_integration(
    mock_config_manager: MockerFixture,
    mock_github_service: MockerFixture,
    domain_mprs: list[mpr.PullRequestMerge],
) -> None:
    """It returns success."""
    config_manager = mock_config_manager.return_value
    github_service = mock_github_service.return_value
    use_case = ghmp.GhMergePrUseCase(config_manager, github_service)
    use_case.action(REPO, domain_mprs[1])

    assert "success message\n" == use_case.output
    github_service.delete_branch_from_repo.assert_called_once()
