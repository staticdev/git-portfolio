"""Test cases for the Github delete branch use case."""
import pytest
from pytest_mock import MockerFixture

import git_portfolio.domain.config as c
import git_portfolio.use_cases.gh_delete_branch as ghdb


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
    mock.return_value.delete_branch_from_repo.return_value = "success message\n"
    return mock


@pytest.fixture
def domain_branch() -> str:
    """Branch fixture."""
    return "my-branch"


def test_action(
    mock_config_manager: MockerFixture,
    mock_github_service: MockerFixture,
    domain_branch: str,
) -> None:
    """It returns success."""
    config_manager = mock_config_manager.return_value
    github_service = mock_github_service.return_value
    use_case = ghdb.GhDeleteBranchUseCase(config_manager, github_service)
    use_case.action(REPO, domain_branch)

    assert "success message\n" == use_case.output
