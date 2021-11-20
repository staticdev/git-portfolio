"""Test cases for the Github list issue use case."""
from __future__ import annotations

import pytest
from pytest_mock import MockerFixture

import git_portfolio.domain.issue as i
import git_portfolio.request_objects.issue_list as il
import git_portfolio.responses as res
import git_portfolio.views as views


REPO = "org/repo"


@pytest.fixture
def domain_issues() -> list[i.Issue]:
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
def mock_github_service(mocker: MockerFixture) -> MockerFixture:
    """Fixture for mocking GithubService."""
    mock = mocker.patch("git_portfolio.github_service.GithubService", autospec=True)
    mock.return_value.list_issues_from_repo.return_value = "success message\n"
    return mock


def test_action_without_parameters(
    mock_github_service: MockerFixture,
    domain_issues: list[i.Issue],
) -> None:
    """It returns a list of issues."""
    github_service = mock_github_service.return_value
    github_service.list_issues_from_repo.return_value = domain_issues

    request = il.build_list_request()
    response = views.issues(REPO, github_service, request)

    assert bool(response) is True
    assert response.value == domain_issues


def test_action_with_filters(
    mock_github_service: MockerFixture,
    domain_issues: list[i.Issue],
) -> None:
    """It returns a list of issues."""
    github_service = mock_github_service.return_value
    github_service.list_issues_from_repo.return_value = domain_issues

    qry_filters = {"state__eq": "open"}
    request = il.build_list_request(filters=qry_filters)
    response = views.issues(REPO, github_service, request)

    assert bool(response) is True
    assert response.value == domain_issues


def test_action_handles_generic_error(
    mock_github_service: MockerFixture,
) -> None:
    """It returns a system error."""
    github_service = mock_github_service.return_value
    github_service.list_issues_from_repo.side_effect = Exception(
        "Just an error message"
    )

    request = il.build_list_request(filters={})
    response = views.issues(REPO, github_service, request)

    assert bool(response) is False
    assert response.value == {
        "type": res.ResponseTypes.SYSTEM_ERROR,
        "message": "Exception: Just an error message",
    }


def test_action_handles_bad_request(
    mock_github_service: MockerFixture,
) -> None:
    """It returns a parameters error."""
    github_service = mock_github_service.return_value

    request = il.build_list_request(filters=5)  # type: ignore
    response = views.issues(REPO, github_service, request)

    assert bool(response) is False
    assert response.value == {
        "type": res.ResponseTypes.PARAMETERS_ERROR,
        "message": "filters: Is not iterable",
    }
