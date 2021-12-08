"""Test cases for the Github create PR use case."""
from __future__ import annotations

import pytest
from pytest_mock import MockerFixture
from tests.conftest import DOMAIN_PRS
from tests.conftest import REPO
from tests.conftest import SUCCESS_MSG
from tests.test_github_service import FakeGithubService

import git_portfolio.domain.config as c
import git_portfolio.request_objects.issue_list as il
import git_portfolio.responses as res
import git_portfolio.use_cases.gh_create_pr as ghcp


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
def mock_views_issues(mocker: MockerFixture) -> MockerFixture:
    """Fixture for mocking views.issues."""
    return mocker.patch(
        "git_portfolio.views.issues",
    )


def test_action(
    mock_config_manager: MockerFixture,
) -> None:
    """It returns success."""
    config_manager = mock_config_manager.return_value
    request = DOMAIN_PRS[0]
    use_case = ghcp.GhCreatePrUseCase(config_manager, FakeGithubService())

    use_case.action(REPO, request, REQUEST_ISSUES)
    response = use_case.responses[0]

    assert isinstance(response, res.ResponseSuccess)
    assert response.value == SUCCESS_MSG


# TODO: improve output when issue list fails
def test_action_link_issue_failed(
    mock_config_manager: MockerFixture,
    mock_views_issues: MockerFixture,
) -> None:
    """It returns success."""
    config_manager = mock_config_manager.return_value
    mock_views_issues.return_value.action.return_value = res.ResponseFailure(
        res.ResponseTypes.PARAMETERS_ERROR, "msg"
    )
    request = DOMAIN_PRS[1]
    use_case = ghcp.GhCreatePrUseCase(config_manager, FakeGithubService())

    use_case.action(REPO, request, REQUEST_ISSUES)
    response = use_case.responses[0]

    assert isinstance(response, res.ResponseSuccess)
    assert response.value == SUCCESS_MSG


def test_action_link_issue(
    mock_config_manager: MockerFixture,
    mock_views_issues: MockerFixture,
) -> None:
    """It returns success."""
    config_manager = mock_config_manager.return_value
    mock_views_issues.return_value.action.return_value = res.ResponseSuccess()
    request = DOMAIN_PRS[1]
    use_case = ghcp.GhCreatePrUseCase(config_manager, FakeGithubService())

    use_case.action(REPO, request, REQUEST_ISSUES)
    response = use_case.responses[0]

    assert isinstance(response, res.ResponseSuccess)
    assert response.value == SUCCESS_MSG


@pytest.mark.e2e
def test_action_link_issue_e2e(
    mock_config_manager: MockerFixture,
) -> None:
    """It returns success."""
    config_manager = mock_config_manager.return_value
    request = DOMAIN_PRS[1]
    use_case = ghcp.GhCreatePrUseCase(config_manager, FakeGithubService())

    use_case.action(REPO, request, REQUEST_ISSUES)
    response = use_case.responses[0]

    assert isinstance(response, res.ResponseSuccess)
    assert response.value == SUCCESS_MSG
