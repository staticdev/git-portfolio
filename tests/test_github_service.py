"""Test cases for the Github service module."""
from typing import List
from unittest.mock import Mock

import github3
import pytest
from pytest_mock import MockerFixture

import git_portfolio.domain.gh_connection_settings as cs
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
def mock_github3_login(mocker: MockerFixture) -> MockerFixture:
    """Fixture for mocking github3.login."""
    return mocker.patch("github3.login", autospec=True)


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
