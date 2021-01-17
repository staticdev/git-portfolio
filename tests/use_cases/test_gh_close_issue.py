"""Test cases for the Github close issue use case."""
import pytest
from pytest_mock import MockerFixture

import git_portfolio.domain.config as c
import git_portfolio.request_objects.issue_list as il
import git_portfolio.responses as res
import git_portfolio.use_cases.gh_close_issue as ghci

REPO = "org/reponame"
REPO2 = "org/reponame2"
REQUEST_ISSUES = il.build_list_request(
    filters={"state__eq": "open", "title__contains": "title"}
)


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
    mock.return_value.close_issues_from_repo.return_value = "success message\n"
    return mock


@pytest.fixture
def mock_gh_list_issue_use_case(mocker: MockerFixture) -> MockerFixture:
    """Fixture for mocking GhListIssueUseCase."""
    return mocker.patch(
        "git_portfolio.use_cases.gh_list_issue.GhListIssueUseCase",
        autospec=True,
    )


def test_execute_for_all_repos(
    mock_config_manager: MockerFixture,
    mock_github_service: MockerFixture,
) -> None:
    """It returns success."""
    config_manager = mock_config_manager.return_value
    github_service = mock_github_service.return_value
    response = ghci.GhCloseIssueUseCase(config_manager, github_service).execute(
        REQUEST_ISSUES
    )

    assert bool(response) is True
    assert "success message\nsuccess message\n" == response.value


def test_execute_for_all_repos_failed(
    mock_config_manager: MockerFixture,
    mock_github_service: MockerFixture,
    mock_gh_list_issue_use_case: MockerFixture,
) -> None:
    """It returns success."""
    config_manager = mock_config_manager.return_value
    github_service = mock_github_service.return_value
    mock_gh_list_issue_use_case.return_value.execute.return_value = res.ResponseFailure(
        res.ResponseTypes.PARAMETERS_ERROR, "msg"
    )
    response = ghci.GhCloseIssueUseCase(config_manager, github_service).execute(
        REQUEST_ISSUES
    )

    assert bool(response) is True
    assert f"{REPO}: no issues closed.\n{REPO2}: no issues closed.\n" == response.value


def test_execute_for_specific_repo(
    mock_config_manager: MockerFixture,
    mock_github_service: MockerFixture,
    mock_gh_list_issue_use_case: MockerFixture,
) -> None:
    """It returns success."""
    config_manager = mock_config_manager.return_value
    github_service = mock_github_service.return_value
    mock_gh_list_issue_use_case.return_value.execute.return_value = (
        res.ResponseSuccess()
    )
    response = ghci.GhCloseIssueUseCase(config_manager, github_service).execute(
        REQUEST_ISSUES, REPO
    )

    assert bool(response) is True
    assert "success message\n" == response.value


def test_execute_for_specific_repo_failed(
    mock_config_manager: MockerFixture,
    mock_github_service: MockerFixture,
    mock_gh_list_issue_use_case: MockerFixture,
) -> None:
    """It returns success."""
    config_manager = mock_config_manager.return_value
    github_service = mock_github_service.return_value
    mock_gh_list_issue_use_case.return_value.execute.return_value = res.ResponseFailure(
        res.ResponseTypes.PARAMETERS_ERROR, "msg"
    )
    response = ghci.GhCloseIssueUseCase(config_manager, github_service).execute(
        REQUEST_ISSUES, REPO
    )

    assert bool(response) is True
    assert f"{REPO}: no issues closed.\n" == response.value
