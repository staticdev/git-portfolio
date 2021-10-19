"""Test cases for the Github create PR use case."""
from __future__ import annotations

import pytest
from pytest_mock import MockerFixture

import git_portfolio.domain.config as c
import git_portfolio.domain.pull_request as pr
import git_portfolio.request_objects.issue_list as il
import git_portfolio.responses as res
import git_portfolio.use_cases.gh_create_pr as ghcp


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
    mock.return_value.create_pull_request_from_repo.return_value = "success message\n"
    return mock


@pytest.fixture
def mock_gh_list_issue_use_case(mocker: MockerFixture) -> MockerFixture:
    """Fixture for mocking GhListIssueUseCase."""
    return mocker.patch(
        "git_portfolio.use_cases.gh_list_issue.GhListIssueUseCase",
        autospec=True,
    )


@pytest.fixture
def domain_prs() -> list[pr.PullRequest]:
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


# TODO: improve output when issue list fails
def test_action_link_issue_failed(
    mock_config_manager: MockerFixture,
    mock_github_service: MockerFixture,
    mock_gh_list_issue_use_case: MockerFixture,
    domain_prs: list[pr.PullRequest],
) -> None:
    """It returns success."""
    config_manager = mock_config_manager.return_value
    github_service = mock_github_service.return_value
    mock_gh_list_issue_use_case.return_value.action.return_value = res.ResponseFailure(
        res.ResponseTypes.PARAMETERS_ERROR, "msg"
    )
    request = domain_prs[1]
    use_case = ghcp.GhCreatePrUseCase(config_manager, github_service)
    use_case.action(REPO, request, REQUEST_ISSUES)

    assert "success message\n" == use_case.output


def test_action(
    mock_config_manager: MockerFixture,
    mock_github_service: MockerFixture,
    domain_prs: list[pr.PullRequest],
) -> None:
    """It returns success."""
    config_manager = mock_config_manager.return_value
    github_service = mock_github_service.return_value
    request = domain_prs[0]
    use_case = ghcp.GhCreatePrUseCase(config_manager, github_service)
    use_case.action(REPO, request, REQUEST_ISSUES)

    assert "success message\n" == use_case.output


def test_action_link_issue(
    mock_config_manager: MockerFixture,
    mock_github_service: MockerFixture,
    mock_gh_list_issue_use_case: MockerFixture,
    domain_prs: list[pr.PullRequest],
) -> None:
    """It returns success."""
    config_manager = mock_config_manager.return_value
    github_service = mock_github_service.return_value
    mock_gh_list_issue_use_case.return_value.action.return_value = res.ResponseSuccess()
    request = domain_prs[1]
    use_case = ghcp.GhCreatePrUseCase(config_manager, github_service)
    use_case.action(REPO, request, REQUEST_ISSUES)

    assert "success message\n" == use_case.output


@pytest.mark.e2e
def test_action_link_issue_e2e(
    mock_config_manager: MockerFixture,
    mock_github_service: MockerFixture,
    domain_prs: list[pr.PullRequest],
) -> None:
    """It returns success."""
    config_manager = mock_config_manager.return_value
    github_service = mock_github_service.return_value
    request = domain_prs[1]
    use_case = ghcp.GhCreatePrUseCase(config_manager, github_service)
    use_case.action(REPO, request, REQUEST_ISSUES)

    assert "success message\n" == use_case.output
