"""Test cases for the Github list issue use case."""
from typing import List

import pytest
from pytest_mock import MockerFixture

import git_portfolio.domain.config as c
import git_portfolio.domain.issue as i
import git_portfolio.request_objects.issue_list as il
import git_portfolio.responses as res
import git_portfolio.use_cases.gh_list_issue as li


@pytest.fixture
def domain_issues() -> List[i.Issue]:
    """Issues fixture."""
    issue_1 = i.Issue(
        0,
        "my title",
        "my body",
        {"testing", "refactor"},
    )
    issue_2 = i.Issue(
        1,
        "my title 2",
        "my body2",
        set(),
    )
    return [issue_1, issue_2]


@pytest.fixture
def mock_config_manager(mocker: MockerFixture) -> MockerFixture:
    """Fixture for mocking CONFIG_MANAGER."""
    mock = mocker.patch("git_portfolio.config_manager.ConfigManager", autospec=True)
    mock.return_value.config = c.Config(
        "", "mytoken", ["staticdev/omg", "staticdev/omg2"]
    )
    return mock


@pytest.fixture
def mock_github_service(mocker: MockerFixture) -> MockerFixture:
    """Fixture for mocking GithubService."""
    mock = mocker.patch("git_portfolio.github_service.GithubService", autospec=True)
    mock.return_value.list_issues_from_repo.return_value = "success message\n"
    return mock


def test_execute_without_parameters(
    mocker: MockerFixture,
    mock_config_manager: MockerFixture,
    mock_github_service: MockerFixture,
    domain_issues: List[i.Issue],
) -> None:
    """It returns a list of issues."""
    repo = mocker.Mock()
    config_manager = mock_config_manager.return_value
    github_service = mock_github_service.return_value
    github_service.list_issues_from_repo.return_value = domain_issues

    request = il.build_list_request()

    response = li.GhListIssueUseCase(config_manager, github_service).execute(
        request, repo
    )

    assert bool(response) is True
    assert response.value == domain_issues


def test_execute_with_filters(
    mocker: MockerFixture,
    mock_config_manager: MockerFixture,
    mock_github_service: MockerFixture,
    domain_issues: List[i.Issue],
) -> None:
    """It returns a list of issues."""
    repo = mocker.Mock()
    config_manager = mock_config_manager.return_value
    github_service = mock_github_service.return_value
    github_service.list_issues_from_repo.return_value = domain_issues

    qry_filters = {"state__eq": "open"}
    request = il.build_list_request(filters=qry_filters)

    response = li.GhListIssueUseCase(config_manager, github_service).execute(
        request, repo
    )

    assert bool(response) is True
    assert response.value == domain_issues


def test_execute_handles_generic_error(
    mocker: MockerFixture,
    mock_config_manager: MockerFixture,
    mock_github_service: MockerFixture,
) -> None:
    """It returns a system error."""
    repo = mocker.Mock()
    config_manager = mock_config_manager.return_value
    github_service = mock_github_service.return_value
    github_service.list_issues_from_repo.side_effect = Exception(
        "Just an error message"
    )

    request = il.build_list_request(filters={})

    response = li.GhListIssueUseCase(config_manager, github_service).execute(
        request, repo
    )

    assert bool(response) is False
    assert response.value == {
        "type": res.ResponseTypes.SYSTEM_ERROR,
        "message": "Exception: Just an error message",
    }


def test_execute_handles_bad_request(
    mocker: MockerFixture,
    mock_config_manager: MockerFixture,
    mock_github_service: MockerFixture,
) -> None:
    """It returns a parameters error."""
    repo = mocker.Mock()
    config_manager = mock_config_manager.return_value
    github_service = mock_github_service.return_value

    request = il.build_list_request(filters=5)  # type: ignore

    response = li.GhListIssueUseCase(config_manager, github_service).execute(
        request, repo
    )

    assert bool(response) is False
    assert response.value == {
        "type": res.ResponseTypes.PARAMETERS_ERROR,
        "message": "filters: Is not iterable",
    }
