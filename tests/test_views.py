"""Test cases for the Github list issue use case."""
from __future__ import annotations

from pytest_mock import MockerFixture
from tests.conftest import DOMAIN_ISSUES
from tests.conftest import REPO
from tests.test_github_service import FakeGithubService

import git_portfolio.request_objects.issue_list as il
import git_portfolio.responses as res
import git_portfolio.views as views


def test_action_without_parameters() -> None:
    """It returns a list of issues."""
    request = il.build_list_request()
    response = views.issues(REPO, FakeGithubService(), request)

    assert isinstance(response, res.ResponseSuccess)
    assert response.value == DOMAIN_ISSUES


def test_action_with_filters() -> None:
    """It returns a list of issues."""
    qry_filters = {"state__eq": "open"}
    request = il.build_list_request(filters=qry_filters)
    response = views.issues(REPO, FakeGithubService(), request)

    assert isinstance(response, res.ResponseSuccess)
    assert response.value == DOMAIN_ISSUES


def test_action_handles_generic_error(mocker: MockerFixture) -> None:
    """It returns a system error."""
    mock = mocker.patch("git_portfolio.github_service.GithubService", autospec=True)
    mock.return_value.list_issues_from_repo.side_effect = Exception(
        "Just an error message"
    )

    request = il.build_list_request(filters={})
    response = views.issues(REPO, mock.return_value, request)

    assert isinstance(response, res.ResponseFailure)
    assert response.value == {
        "type": res.ResponseTypes.SYSTEM_ERROR,
        "message": "Exception: Just an error message",
    }


def test_action_handles_bad_request() -> None:
    """It returns a parameters error."""
    request = il.build_list_request(filters=5)  # type: ignore
    response = views.issues(REPO, FakeGithubService(), request)

    assert isinstance(response, res.ResponseFailure)
    assert response.value == {
        "type": res.ResponseTypes.PARAMETERS_ERROR,
        "message": "filters: Is not iterable",
    }
