"""Test cases for the Github merge PR use case."""
from __future__ import annotations

import pytest
from pytest_mock import MockerFixture
from tests.conftest import REPO

import git_portfolio.domain.config as c
import git_portfolio.domain.pull_request_merge as mpr
import git_portfolio.github_service as gs
import git_portfolio.responses as res
import git_portfolio.use_cases.gh_merge_pr as ghmp


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
    response = use_case.responses[0]

    assert isinstance(response, res.ResponseSuccess)
    assert "success message\n" == response.value


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
    response = use_case.responses[0]

    assert isinstance(response, res.ResponseSuccess)
    assert "success message\n" == response.value
    mock_gh_delete_branch_use_case.assert_called_once()


def test_action_delete_branch_with_error(
    mock_config_manager: MockerFixture,
    mock_github_service: MockerFixture,
    mock_gh_delete_branch_use_case: MockerFixture,
    domain_mprs: list[mpr.PullRequestMerge],
) -> None:
    """It returns does not call delete branch."""
    config_manager = mock_config_manager.return_value
    github_service = mock_github_service.return_value
    use_case = ghmp.GhMergePrUseCase(config_manager, github_service)
    github_service.merge_pull_request_from_repo.side_effect = gs.GithubServiceError

    use_case.action(REPO, domain_mprs[1])
    response = use_case.responses[0]

    assert isinstance(response, res.ResponseFailure)
    assert not mock_gh_delete_branch_use_case.called


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
    response = use_case.responses[0]

    assert isinstance(response, res.ResponseSuccess)
    assert "success message\n" == response.value
    github_service.delete_branch_from_repo.assert_called_once()
