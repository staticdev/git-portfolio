"""Test cases for the Github reopen issue use case."""
import pytest
from pytest_mock import MockerFixture

import git_portfolio.domain.config as c
import git_portfolio.request_objects.issue_list as il
import git_portfolio.responses as res
import git_portfolio.use_cases.gh_reopen_issue as ghri
from tests.conftest import REPO


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
    mock.return_value.reopen_issues_from_repo.return_value = "success message\n"
    return mock


@pytest.fixture
def mock_views_issues(mocker: MockerFixture) -> MockerFixture:
    """Fixture for mocking views.issues."""
    return mocker.patch(
        "git_portfolio.views.issues",
    )


def test_action(
    mock_config_manager: MockerFixture,
    mock_github_service: MockerFixture,
    mock_views_issues: MockerFixture,
) -> None:
    """It returns success."""
    config_manager = mock_config_manager.return_value
    github_service = mock_github_service.return_value
    mock_views_issues.return_value = res.ResponseSuccess()
    use_case = ghri.GhReopenIssueUseCase(config_manager, github_service)

    use_case.action(REPO, REQUEST_ISSUES)
    response = use_case.responses[0]

    assert isinstance(response, res.ResponseSuccess)
    assert "success message\n" == response.value


def test_action_failed(
    mock_config_manager: MockerFixture,
    mock_github_service: MockerFixture,
    mock_views_issues: MockerFixture,
) -> None:
    """It returns error."""
    config_manager = mock_config_manager.return_value
    github_service = mock_github_service.return_value
    mock_views_issues.return_value = res.ResponseFailure(
        res.ResponseTypes.RESOURCE_ERROR, "msg"
    )
    use_case = ghri.GhReopenIssueUseCase(config_manager, github_service)

    use_case.action(REPO, REQUEST_ISSUES)
    response = use_case.responses[0]

    assert isinstance(response, res.ResponseFailure)
    assert f"{REPO}: no issues match search.\n" == response.value["message"]
