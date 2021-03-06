"""Test cases for the Github close issue use case."""
import pytest
from pytest_mock import MockerFixture

import git_portfolio.domain.config as c
import git_portfolio.request_objects.issue_list as il
import git_portfolio.responses as res
import git_portfolio.use_cases.gh_close_issue as ghci


REPO = "org/repo-name"
REQUEST_ISSUES = il.build_list_request(
    filters={"state__eq": "open", "title__contains": "title"}
)


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
    mock.return_value.close_issues_from_repo.return_value = "success message\n"
    return mock


@pytest.fixture
def mock_gh_list_issue_use_case(mocker: MockerFixture) -> MockerFixture:
    """Fixture for mocking GhListIssueUseCase."""
    return mocker.patch(
        "git_portfolio.use_cases.gh_list_issue.GhListIssueUseCase",
        autospec=True,
    )


def test_action(
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
    use_case = ghci.GhCloseIssueUseCase(config_manager, github_service)
    use_case.action(REPO, REQUEST_ISSUES)

    assert "success message\n" == use_case.output


def test_action_failed(
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
    use_case = ghci.GhCloseIssueUseCase(config_manager, github_service)
    use_case.action(REPO, REQUEST_ISSUES)

    assert f"{REPO}: no issues match search.\n" == use_case.output
