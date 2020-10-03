"""Test cases for the Github service module."""
from typing import List
from unittest.mock import Mock

import github3
import pytest
from pytest_mock import MockerFixture

import git_portfolio.domain.gh_connection_settings as cs
import git_portfolio.domain.issue as i
import git_portfolio.github_service as gc


@pytest.fixture
def domain_gh_conn_settings() -> List[cs.GhConnectionSettings]:
    """Issue fixture."""
    gh_conn_settings = [
        cs.GhConnectionSettings(
            "mytoken",
            "",
        ),
        cs.GhConnectionSettings(
            "mytoken",
            "myhost.com",
        ),
    ]
    return gh_conn_settings


@pytest.fixture
def domain_issue() -> i.Issue:
    """Issue fixture."""
    issue = i.Issue(
        "my title",
        "my body",
        {"testing", "refactor"},
    )
    return issue


@pytest.fixture
def domain_branch() -> str:
    """Branch fixture."""
    return "my-branch"


@pytest.fixture
def mock_github3_login(mocker: MockerFixture) -> MockerFixture:
    """Fixture for mocking github3.login."""
    mock = mocker.patch("github3.login", autospec=True)
    mock.return_value.repositories.return_value = [
        Mock(full_name="staticdev/nope"),
        Mock(full_name="staticdev/omg"),
    ]
    return mock


@pytest.fixture
def mock_github3_enterprise_login(mocker: MockerFixture) -> MockerFixture:
    """Fixture for mocking github3.enterprise_login."""
    return mocker.patch("github3.enterprise_login", autospec=True)


def test_init_github_com(
    domain_gh_conn_settings: List[cs.GhConnectionSettings],
    mock_github3_login: MockerFixture,
) -> None:
    """It succeeds."""
    gc.GithubService(domain_gh_conn_settings[0])


def test_init_github_entreprise(
    domain_gh_conn_settings: List[cs.GhConnectionSettings],
    mock_github3_enterprise_login: MockerFixture,
) -> None:
    """It succeeds."""
    gc.GithubService(domain_gh_conn_settings[1])


def test_init_wrong_token(
    domain_gh_conn_settings: List[cs.GhConnectionSettings],
    mock_github3_login: MockerFixture,
) -> None:
    """It succeeds."""
    mock_github3_login.return_value.me.side_effect = (
        github3.exceptions.AuthenticationFailed(Mock())
    )
    with pytest.raises(AttributeError):
        gc.GithubService(domain_gh_conn_settings[0])


def test_init_connection_error(
    domain_gh_conn_settings: List[cs.GhConnectionSettings],
    mock_github3_login: MockerFixture,
) -> None:
    """It succeeds."""
    mock_github3_login.return_value.me.side_effect = github3.exceptions.ConnectionError(
        Mock()
    )
    with pytest.raises(ConnectionError):
        gc.GithubService(domain_gh_conn_settings[0])


def test_create_issue_from_repo_success(
    domain_gh_conn_settings: List[cs.GhConnectionSettings],
    mock_github3_login: MockerFixture,
    domain_issue: i.Issue,
) -> None:
    """It succeeds."""
    response = gc.GithubService(domain_gh_conn_settings[0]).create_issue_from_repo(
        "staticdev/omg", domain_issue
    )

    assert response == "staticdev/omg: issue created successfully."


def test_create_issue_from_repo_fork(
    domain_gh_conn_settings: List[cs.GhConnectionSettings],
    mock_github3_login: MockerFixture,
    domain_issue: i.Issue,
) -> None:
    """It gives a message error telling it is a fork."""
    exception_mock = Mock()
    exception_mock.json.return_value.get.return_value = (
        "Issues are disabled for this repo"
    )
    mock_github3_login.return_value.repositories.return_value[
        1
    ].create_issue.side_effect = github3.exceptions.ClientError(exception_mock)
    response = gc.GithubService(domain_gh_conn_settings[0]).create_issue_from_repo(
        "staticdev/omg", domain_issue
    )

    assert (
        response
        == "staticdev/omg: Issues are disabled for this repo. It may be a fork."
    )


def test_create_issue_from_repo_other_error(
    domain_gh_conn_settings: List[cs.GhConnectionSettings],
    mock_github3_login: MockerFixture,
    domain_issue: i.Issue,
) -> None:
    """It gives the message error returned from the API."""
    exception_mock = Mock()
    exception_mock.json.return_value.get.return_value = "returned message"
    mock_github3_login.return_value.repositories.return_value[
        1
    ].create_issue.side_effect = github3.exceptions.ClientError(exception_mock)
    response = gc.GithubService(domain_gh_conn_settings[0]).create_issue_from_repo(
        "staticdev/omg", domain_issue
    )

    assert response == "staticdev/omg: returned message."


def test_delete_branch_from_repo_success(
    domain_gh_conn_settings: List[cs.GhConnectionSettings],
    mock_github3_login: MockerFixture,
    domain_branch: str,
) -> None:
    """It succeeds."""
    response = gc.GithubService(domain_gh_conn_settings[0]).delete_branch_from_repo(
        "staticdev/omg", domain_branch
    )

    assert response == "staticdev/omg: branch deleted successfully."


def test_delete_branch_from_repo_branch_not_found(
    domain_gh_conn_settings: List[cs.GhConnectionSettings],
    mock_github3_login: MockerFixture,
    domain_branch: str,
) -> None:
    """It gives the message error returned from the API."""
    exception_mock = Mock()
    exception_mock.json.return_value.get.return_value = "Branch not found"
    mock_github3_login.return_value.repositories.return_value[
        1
    ].branch.side_effect = github3.exceptions.NotFoundError(exception_mock)
    response = gc.GithubService(domain_gh_conn_settings[0]).delete_branch_from_repo(
        "staticdev/omg", domain_branch
    )

    assert response == "staticdev/omg: Branch not found."
