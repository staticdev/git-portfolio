"""Test cases for the Github service module."""
from __future__ import annotations

import unittest

import github3
import pytest
from pytest_mock import MockerFixture
from tests.conftest import BRANCH_NAME
from tests.conftest import DOMAIN_ISSUES
from tests.conftest import DOMAIN_MPR
from tests.conftest import DOMAIN_PRS
from tests.conftest import ERROR_MSG
from tests.conftest import LABEL_BUG
from tests.conftest import LABEL_DO_NOT_INHERIT
from tests.conftest import LABEL_ENHANCEMENT
from tests.conftest import REPO
from tests.conftest import REPO2
from tests.conftest import SUCCESS_MSG

import git_portfolio.domain.gh_connection_settings as cs
import git_portfolio.domain.issue as i
import git_portfolio.domain.pull_request as pr
import git_portfolio.github_service as gs
import git_portfolio.request_objects.issue_list as il


class FakeGithubService(gs.AbstractGithubService):
    """Fake Github Service."""

    def fake_success(self, _: str) -> str:
        """Fake success method."""
        return SUCCESS_MSG

    def fake_error(self, _: str) -> str:
        """Fake expected error method."""
        raise gs.GithubServiceError(ERROR_MSG)

    def fake_unexpected_error(self, _: str) -> str:
        """Fake expected error method."""
        raise Exception(ERROR_MSG)

    def create_pull_request_from_repo(self, _: str, __: pr.PullRequest) -> str:
        """Fake create pull request from one repository."""
        return SUCCESS_MSG

    def list_issues_from_repo(
        self, _: str, __: il.IssueListValidRequest | il.IssueListInvalidRequest
    ) -> list[i.Issue]:
        """Fake issues list method."""
        return DOMAIN_ISSUES

    @staticmethod
    def link_issues(_: pr.PullRequest, __: list[i.Issue]) -> pr.PullRequest:
        """Fake link issues method."""
        return pr.PullRequest(
            "Title", "", set(), False, "query", False, "main", "origin", False
        )


@pytest.fixture
def domain_gh_conn_settings() -> list[cs.GhConnectionSettings]:
    """Github connection settings fixture."""
    gh_conn_settings = [
        cs.GhConnectionSettings(
            "my-token",
            "",
        ),
        cs.GhConnectionSettings(
            "my-token",
            "myhost.com",
        ),
    ]
    return gh_conn_settings


@pytest.fixture
def mock_github3_login(mocker: MockerFixture) -> MockerFixture:
    """Fixture for mocking github3.login."""
    mock_repo = mocker.Mock(full_name=REPO)
    mock_repo2 = mocker.Mock(full_name=REPO2)

    mock = mocker.patch("github3.login", autospec=True)
    mock.return_value.repositories.return_value = [
        mock_repo2,
        mock_repo,
    ]
    return mock


@pytest.fixture
def mock_github3_enterprise_login(mocker: MockerFixture) -> MockerFixture:
    """Fixture for mocking github3.enterprise_login."""
    return mocker.patch("github3.enterprise_login", autospec=True)


# Details on mocking exception constructor at
# stackoverflow.com/questions/64226516/how-to-set-mocked-exception-behavior-on-python
@pytest.fixture
def mock_github3_unprocessable_entity_exception(mocker: MockerFixture) -> MockerFixture:
    """Fixture for mocking github3.exceptions.UnprocessableEntity."""

    def _initiate_mocked_exception(
        self: github3.exceptions.UnprocessableEntity,
    ) -> None:
        self.errors = [{"message": ERROR_MSG}]
        self.msg = "Validation Failed"

    return mocker.patch.object(
        github3.exceptions.UnprocessableEntity, "__init__", _initiate_mocked_exception
    )


def test_init_github_com(
    domain_gh_conn_settings: list[cs.GhConnectionSettings],
    mock_github3_login: MockerFixture,
) -> None:
    """It succeeds."""
    gs.GithubService(domain_gh_conn_settings[0])


def test_init_github_entreprise(
    domain_gh_conn_settings: list[cs.GhConnectionSettings],
    mock_github3_enterprise_login: MockerFixture,
) -> None:
    """It succeeds."""
    gs.GithubService(domain_gh_conn_settings[1])


def test_init_invalid_token(
    mocker: MockerFixture,
    domain_gh_conn_settings: list[cs.GhConnectionSettings],
    mock_github3_login: MockerFixture,
) -> None:
    """It returns invalid token message."""
    mock_github3_login.return_value.me.side_effect = (
        github3.exceptions.AuthenticationFailed(mocker.Mock())
    )
    with pytest.raises(
        gs.GithubServiceError,
        match="Wrong GitHub permissions. Please check your token.",
    ):
        gs.GithubService(domain_gh_conn_settings[0])


def test_init_invalid_token_scope(
    mocker: MockerFixture,
    domain_gh_conn_settings: list[cs.GhConnectionSettings],
    mock_github3_login: MockerFixture,
) -> None:
    """It returns invalid response message."""
    mock_github3_login.return_value.me.side_effect = (
        github3.exceptions.IncompleteResponse(mocker.Mock(), mocker.Mock())
    )
    with pytest.raises(gs.GithubServiceError) as excinfo:
        gs.GithubService(domain_gh_conn_settings[0])

    assert "Invalid response. Your token might not be properly scoped." == str(
        excinfo.value
    )


def test_init_connection_error(
    mocker: MockerFixture,
    domain_gh_conn_settings: list[cs.GhConnectionSettings],
    mock_github3_login: MockerFixture,
) -> None:
    """It succeeds."""
    mock_github3_login.return_value.me.side_effect = github3.exceptions.ConnectionError(
        mocker.Mock()
    )
    with pytest.raises(gs.GithubServiceError):
        gs.GithubService(domain_gh_conn_settings[0])


def test_get_config(
    domain_gh_conn_settings: list[cs.GhConnectionSettings],
    mock_github3_login: MockerFixture,
) -> None:
    """It returns service config."""
    expected = domain_gh_conn_settings[0]
    result = gs.GithubService(domain_gh_conn_settings[0]).get_config()

    assert result == expected


def test_get_repo_no_repo(
    mocker: MockerFixture, domain_gh_conn_settings: list[cs.GhConnectionSettings]
) -> None:
    """It returns None."""
    mock = mocker.patch("github3.login", autospec=True)
    mock.return_value.repositories.return_value = []

    with pytest.raises(NameError):
        gs.GithubService(domain_gh_conn_settings[0])._get_repo(REPO)


def test_get_repo_url_success(
    mocker: MockerFixture,
    domain_gh_conn_settings: list[cs.GhConnectionSettings],
    mock_github3_login: MockerFixture,
) -> None:
    """It returns url."""
    expected = f"git@github.com:{REPO}.git"
    result = gs.GithubService(domain_gh_conn_settings[0]).get_repo_url(REPO)

    assert result == expected


def test_get_repo_url_no_repo(
    mocker: MockerFixture, domain_gh_conn_settings: list[cs.GhConnectionSettings]
) -> None:
    """It returns None."""
    mock = mocker.patch("github3.login", autospec=True)
    mock.return_value.repositories.return_value = []

    with pytest.raises(NameError):
        gs.GithubService(domain_gh_conn_settings[0]).get_repo_url(REPO)


def test_get_repo_names(
    domain_gh_conn_settings: list[cs.GhConnectionSettings],
    mock_github3_login: MockerFixture,
) -> None:
    """It returns list of strings."""
    expected = [REPO2, REPO]
    result = gs.GithubService(domain_gh_conn_settings[0]).get_repo_names()

    assert result == expected


def test_get_username(
    domain_gh_conn_settings: list[cs.GhConnectionSettings],
    mock_github3_login: MockerFixture,
) -> None:
    """It returns user name."""
    expected = "user"
    mock_github3_login.return_value.me.return_value.login = "user"
    result = gs.GithubService(domain_gh_conn_settings[0]).get_username()

    assert result == expected


def test_create_issue_from_repo_success(
    domain_gh_conn_settings: list[cs.GhConnectionSettings],
    mock_github3_login: MockerFixture,
) -> None:
    """It succeeds."""
    response = gs.GithubService(domain_gh_conn_settings[0]).create_issue_from_repo(
        REPO, DOMAIN_ISSUES[0]
    )

    assert response == f"{REPO}: create issue successful.\n"


def test_create_issue_from_repo_fork(
    mocker: MockerFixture,
    domain_gh_conn_settings: list[cs.GhConnectionSettings],
    mock_github3_login: MockerFixture,
) -> None:
    """It gives a message error telling it is a fork."""
    exception_mock = mocker.Mock()
    exception_mock.json.return_value.get.return_value = (
        "Issues are disabled for this repo"
    )
    repo = mock_github3_login.return_value.repositories.return_value[1]
    repo.create_issue.side_effect = github3.exceptions.ClientError(exception_mock)
    response = gs.GithubService(domain_gh_conn_settings[0]).create_issue_from_repo(
        REPO, DOMAIN_ISSUES[0]
    )

    assert response == f"{REPO}: Issues are disabled for this repo. It may be a fork.\n"


def test_create_issue_from_repo_other_client_error(
    mocker: MockerFixture,
    domain_gh_conn_settings: list[cs.GhConnectionSettings],
    mock_github3_login: MockerFixture,
) -> None:
    """It gives the message error returned from the API."""
    exception_mock = mocker.Mock()
    exception_mock.json.return_value.get.return_value = "returned message"
    repo = mock_github3_login.return_value.repositories.return_value[1]
    repo.create_issue.side_effect = github3.exceptions.ClientError(exception_mock)
    response = gs.GithubService(domain_gh_conn_settings[0]).create_issue_from_repo(
        REPO, DOMAIN_ISSUES[0]
    )

    assert response == f"{REPO}: returned message.\n"


def test_create_issue_from_repo_other_error(
    mocker: MockerFixture,
    domain_gh_conn_settings: list[cs.GhConnectionSettings],
    mock_github3_login: MockerFixture,
) -> None:
    """It gives the message error returned from the API."""
    exception_mock = mocker.Mock()
    exception_mock.json.return_value.get.return_value = "returned message"
    repo = mock_github3_login.return_value.repositories.return_value[1]
    repo.create_issue.side_effect = github3.exceptions.ForbiddenError(exception_mock)

    with pytest.raises(gs.GithubServiceError, match=f"{REPO}: returned message"):
        gs.GithubService(domain_gh_conn_settings[0]).create_issue_from_repo(
            REPO, DOMAIN_ISSUES[0]
        )


def test_list_issues_from_repo_title_filter(
    mocker: MockerFixture,
    domain_gh_conn_settings: list[cs.GhConnectionSettings],
    mock_github3_login: MockerFixture,
) -> None:
    """It succeeds."""
    label1 = mocker.Mock()
    label1.name = LABEL_DO_NOT_INHERIT
    label2 = mocker.Mock()
    label2.name = LABEL_ENHANCEMENT
    label3 = mocker.Mock()
    label3.name = LABEL_BUG

    issue1 = mocker.Mock(number=DOMAIN_ISSUES[1].number, title=DOMAIN_ISSUES[1].title)
    issue1.labels.return_value = [label1]
    issue2 = mocker.Mock(number=DOMAIN_ISSUES[2].number, title=DOMAIN_ISSUES[2].title)
    issue2.labels.return_value = []
    issue3 = mocker.Mock(number=DOMAIN_ISSUES[3].number, title=DOMAIN_ISSUES[3].title)
    issue3.labels.return_value = [label2, label3]

    repo = mock_github3_login.return_value.repositories.return_value[1]
    repo.issues.return_value = [
        issue1,
        issue2,
        issue3,
    ]

    title_filtered_request = il.IssueListValidRequest(
        filters={"state__eq": "open", "title__contains": "issue title"}
    )

    response = gs.GithubService(domain_gh_conn_settings[0]).list_issues_from_repo(
        REPO, title_filtered_request
    )

    assert len(response) == 2
    assert response[0].number == DOMAIN_ISSUES[2].number
    assert response[0].title == DOMAIN_ISSUES[2].title
    assert response[1].number == DOMAIN_ISSUES[3].number
    assert response[1].title == DOMAIN_ISSUES[3].title


@pytest.mark.parametrize("value", ["issue", "pull request"])
def test_list_issues_from_repo_obj_filter(
    value: str,
    mocker: MockerFixture,
    domain_gh_conn_settings: list[cs.GhConnectionSettings],
    mock_github3_login: MockerFixture,
) -> None:
    """It succeeds."""
    label1 = mocker.Mock()
    label1.name = LABEL_ENHANCEMENT
    label2 = mocker.Mock()
    label2.name = LABEL_BUG

    issue1 = mocker.Mock(
        number=DOMAIN_ISSUES[2].number,
        title=DOMAIN_ISSUES[2].title,
        pull_request_urls=None,
    )
    issue1.labels.return_value = []
    issue2 = mocker.Mock(
        number=DOMAIN_ISSUES[3].number,
        title=DOMAIN_ISSUES[3].title,
        pull_request_urls="something",
    )
    issue2.labels.return_value = [label1, label2]

    repo = mock_github3_login.return_value.repositories.return_value[1]
    repo.issues.return_value = [
        issue1,
        issue2,
    ]

    obj_filtered_request = il.IssueListValidRequest(
        filters={"state__eq": "open", "obj__eq": value}
    )

    response = gs.GithubService(domain_gh_conn_settings[0]).list_issues_from_repo(
        REPO, obj_filtered_request
    )

    assert len(response) == 1
    if value == "issue":
        assert response[0].number == DOMAIN_ISSUES[2].number
        assert response[0].title == DOMAIN_ISSUES[2].title
    if value == "pull request":
        assert response[0].number == DOMAIN_ISSUES[3].number
        assert response[0].title == DOMAIN_ISSUES[3].title


def test_list_issues_from_repo_no_filter_request(
    mocker: MockerFixture,
    domain_gh_conn_settings: list[cs.GhConnectionSettings],
    mock_github3_login: MockerFixture,
) -> None:
    """It returns empty result."""
    issue1 = mocker.Mock(number=DOMAIN_ISSUES[0].number, title=DOMAIN_ISSUES[0].title)
    issue1.labels.return_value = []
    issue2 = mocker.Mock(number=DOMAIN_ISSUES[1].number, title=DOMAIN_ISSUES[1].title)
    issue2.labels.return_value = []
    repo = mock_github3_login.return_value.repositories.return_value[1]
    repo.issues.return_value = [
        issue1,
        issue2,
    ]

    response = gs.GithubService(domain_gh_conn_settings[0]).list_issues_from_repo(
        REPO, il.IssueListValidRequest()
    )

    assert len(response) == 2
    assert response[0].number == DOMAIN_ISSUES[0].number
    assert response[0].title == DOMAIN_ISSUES[0].title
    assert response[1].number == DOMAIN_ISSUES[1].number
    assert response[1].title == DOMAIN_ISSUES[1].title


def test_close_issues_from_repo_success(
    domain_gh_conn_settings: list[cs.GhConnectionSettings],
    mock_github3_login: MockerFixture,
) -> None:
    """It succeeds."""
    mock_github3_login.return_value.issue().is_closed.return_value = False
    response = gs.GithubService(domain_gh_conn_settings[0]).close_issues_from_repo(
        REPO, DOMAIN_ISSUES
    )

    assert response == f"{REPO}: close issues successful.\n"


def test_close_issues_from_repo_no_issue(
    domain_gh_conn_settings: list[cs.GhConnectionSettings],
    mock_github3_login: MockerFixture,
) -> None:
    """It returns a not issue message."""
    mock_github3_login.return_value.issue().is_closed.return_value = False
    response = gs.GithubService(domain_gh_conn_settings[0]).close_issues_from_repo(
        REPO, []
    )

    assert response == f"{REPO}: no issues match.\n"


def test_close_issues_from_repo_already_closed(
    domain_gh_conn_settings: list[cs.GhConnectionSettings],
    mock_github3_login: MockerFixture,
) -> None:
    """It succeeds."""
    mock_github3_login.return_value.issue().is_closed.return_value = True
    response = gs.GithubService(domain_gh_conn_settings[0]).close_issues_from_repo(
        REPO, DOMAIN_ISSUES
    )

    assert response == f"{REPO}: close issues successful.\n"


def test_reopen_issues_from_repo_success(
    domain_gh_conn_settings: list[cs.GhConnectionSettings],
    mock_github3_login: MockerFixture,
) -> None:
    """It succeeds."""
    response = gs.GithubService(domain_gh_conn_settings[0]).reopen_issues_from_repo(
        REPO, DOMAIN_ISSUES
    )

    assert response == f"{REPO}: reopen issues successful.\n"


def test_reopen_issues_from_repo_no_issue(
    domain_gh_conn_settings: list[cs.GhConnectionSettings],
    mock_github3_login: MockerFixture,
) -> None:
    """It returns a not issue message."""
    response = gs.GithubService(domain_gh_conn_settings[0]).reopen_issues_from_repo(
        REPO, []
    )

    assert response == f"{REPO}: no issues match.\n"


def test_reopen_issues_from_repo_error(
    mock_github3_unprocessable_entity_exception: MockerFixture,
    domain_gh_conn_settings: list[cs.GhConnectionSettings],
    mock_github3_login: MockerFixture,
) -> None:
    """It returns a not issue message."""
    repo = mock_github3_login.return_value.issue.return_value
    repo.reopen.side_effect = github3.exceptions.UnprocessableEntity

    with pytest.raises(gs.GithubServiceError):
        gs.GithubService(domain_gh_conn_settings[0]).reopen_issues_from_repo(
            REPO, DOMAIN_ISSUES
        )


def test_create_pull_request_from_repo_success(
    domain_gh_conn_settings: list[cs.GhConnectionSettings],
    mock_github3_login: MockerFixture,
) -> None:
    """It succeeds."""
    response = gs.GithubService(
        domain_gh_conn_settings[0]
    ).create_pull_request_from_repo(REPO, DOMAIN_PRS[0])

    assert response == f"{REPO}: create PR successful.\n"


def test_create_pull_request_from_repo_with_labels(
    domain_gh_conn_settings: list[cs.GhConnectionSettings],
    mock_github3_login: MockerFixture,
) -> None:
    """It succeeds."""
    response = gs.GithubService(
        domain_gh_conn_settings[0]
    ).create_pull_request_from_repo(REPO, DOMAIN_PRS[1])

    assert response == f"{REPO}: create PR successful.\n"


def test_create_pull_request_from_repo_no_commits(
    mocker: MockerFixture,
    mock_github3_unprocessable_entity_exception: MockerFixture,
    domain_gh_conn_settings: list[cs.GhConnectionSettings],
    mock_github3_login: MockerFixture,
) -> None:
    """It gives the message error from the exception."""
    repo = mock_github3_login.return_value.repositories.return_value[1]
    repo.create_pull.side_effect = github3.exceptions.UnprocessableEntity
    response = gs.GithubService(
        domain_gh_conn_settings[0]
    ).create_pull_request_from_repo(REPO, DOMAIN_PRS[1])

    assert response == (f"{REPO}: Validation Failed. {ERROR_MSG}.\n")


def test_create_pull_request_from_repo_invalid_branch(
    mocker: MockerFixture,
    domain_gh_conn_settings: list[cs.GhConnectionSettings],
    mock_github3_login: MockerFixture,
) -> None:
    """It gives the message error informing the invalid field head."""

    def _initiate_mocked_exception(
        self: github3.exceptions.UnprocessableEntity,
    ) -> None:
        self.errors = [{"field": "head"}]
        self.msg = "Validation Failed"

    mocker.patch.object(
        github3.exceptions.UnprocessableEntity, "__init__", _initiate_mocked_exception
    )

    repo = mock_github3_login.return_value.repositories.return_value[1]
    repo.create_pull.side_effect = github3.exceptions.UnprocessableEntity
    response = gs.GithubService(
        domain_gh_conn_settings[0]
    ).create_pull_request_from_repo(REPO, DOMAIN_PRS[1])

    assert response == f"{REPO}: Validation Failed. Invalid field head.\n"


def test_create_pull_request_from_repo_other_error(
    mocker: MockerFixture,
    domain_gh_conn_settings: list[cs.GhConnectionSettings],
    mock_github3_login: MockerFixture,
) -> None:
    """It gives the message error returned from the API."""
    exception_mock = mocker.Mock()
    exception_mock.json.return_value.get.return_value = "returned message"
    repo = mock_github3_login.return_value.repositories.return_value[1]
    repo.create_pull.side_effect = github3.exceptions.ForbiddenError(exception_mock)

    with pytest.raises(gs.GithubServiceError, match=f"{REPO}: returned message"):
        gs.GithubService(domain_gh_conn_settings[0]).create_pull_request_from_repo(
            REPO, DOMAIN_PRS[0]
        )


def test_link_issue_success(
    domain_gh_conn_settings: list[cs.GhConnectionSettings],
    mock_github3_login: MockerFixture,
) -> None:
    """It succeeds."""
    pr = gs.GithubService(domain_gh_conn_settings[0]).link_issues(
        DOMAIN_PRS[1], DOMAIN_ISSUES[2:]
    )

    assert pr.body == f"{DOMAIN_PRS[1].body}\n\nCloses #2\nCloses #3\n"
    case = unittest.TestCase()
    case.assertCountEqual(DOMAIN_PRS[1].labels, {LABEL_BUG})
    case.assertCountEqual(pr.labels, {LABEL_BUG, LABEL_ENHANCEMENT})


def test_link_issue_no_link(
    domain_gh_conn_settings: list[cs.GhConnectionSettings],
    mock_github3_login: MockerFixture,
) -> None:
    """It succeeds without any linked issue."""
    gs.GithubService(domain_gh_conn_settings[0]).link_issues(DOMAIN_PRS[1], [])

    assert DOMAIN_PRS[1].body == "my pr body 2"


def test_delete_branch_from_repo_success(
    mocker: MockerFixture,
    domain_gh_conn_settings: list[cs.GhConnectionSettings],
    mock_github3_login: MockerFixture,
) -> None:
    """It succeeds."""
    response = gs.GithubService(domain_gh_conn_settings[0]).delete_branch_from_repo(
        REPO, BRANCH_NAME
    )

    assert response == f"{REPO}: delete branch successful.\n"


def test_delete_branch_from_repo_branch_not_found(
    mocker: MockerFixture,
    domain_gh_conn_settings: list[cs.GhConnectionSettings],
    mock_github3_login: MockerFixture,
) -> None:
    """It gives the message error returned from the API."""

    def _initiate_mocked_exception(
        self: github3.exceptions.NotFoundError,
    ) -> None:
        self.msg = "Not found"

    mocker.patch.object(
        github3.exceptions.NotFoundError, "__init__", _initiate_mocked_exception
    )

    repo = mock_github3_login.return_value.repositories.return_value[1]
    repo.ref.side_effect = github3.exceptions.NotFoundError

    response = gs.GithubService(domain_gh_conn_settings[0]).delete_branch_from_repo(
        REPO, BRANCH_NAME
    )

    assert response == f"{REPO}: Not found.\n"


def test_delete_branch_from_repo_other_error(
    mocker: MockerFixture,
    domain_gh_conn_settings: list[cs.GhConnectionSettings],
    mock_github3_login: MockerFixture,
) -> None:
    """It gives the message error returned from the API."""
    exception_mock = mocker.Mock()
    exception_mock.json.return_value.get.return_value = "returned message"
    repo = mock_github3_login.return_value.repositories.return_value[1]
    repo.ref.side_effect = github3.exceptions.ForbiddenError(exception_mock)

    with pytest.raises(gs.GithubServiceError, match=f"{REPO}: returned message"):
        gs.GithubService(domain_gh_conn_settings[0]).delete_branch_from_repo(
            REPO, BRANCH_NAME
        )


def test_merge_pull_request_from_repo_success(
    mocker: MockerFixture,
    domain_gh_conn_settings: list[cs.GhConnectionSettings],
    mock_github3_login: MockerFixture,
) -> None:
    """It succeeds."""
    repo = mock_github3_login.return_value.repositories.return_value[1]
    repo.pull_requests.return_value = [mocker.Mock()]
    response = gs.GithubService(
        domain_gh_conn_settings[0]
    ).merge_pull_request_from_repo(REPO, DOMAIN_MPR)

    assert response == f"{REPO}: merge PR successful.\n"


def test_merge_pull_request_from_repo_error_merging(
    mocker: MockerFixture,
    domain_gh_conn_settings: list[cs.GhConnectionSettings],
    mock_github3_login: MockerFixture,
) -> None:
    """It throws exception."""
    repo = mock_github3_login.return_value.repositories.return_value[1]
    pr = mocker.Mock()
    pr.merge.side_effect = github3.exceptions.MethodNotAllowed(mocker.Mock())
    repo.pull_requests.return_value = [pr]
    with pytest.raises(gs.GithubServiceError):
        gs.GithubService(domain_gh_conn_settings[0]).merge_pull_request_from_repo(
            REPO, DOMAIN_MPR
        )


def test_merge_pull_request_from_repo_not_found(
    domain_gh_conn_settings: list[cs.GhConnectionSettings],
    mock_github3_login: MockerFixture,
) -> None:
    """It gives error message."""
    repo = mock_github3_login.return_value.repositories.return_value[1]
    repo.pull_requests.return_value = []

    with pytest.raises(
        gs.GithubServiceError, match=f"{REPO}: no open PR found for branch:main.\n"
    ):
        gs.GithubService(domain_gh_conn_settings[0]).merge_pull_request_from_repo(
            REPO, DOMAIN_MPR
        )


def test_merge_pull_request_from_repo_ambiguous(
    mocker: MockerFixture,
    domain_gh_conn_settings: list[cs.GhConnectionSettings],
    mock_github3_login: MockerFixture,
) -> None:
    """It gives error message."""
    repo = mock_github3_login.return_value.repositories.return_value[1]
    repo.pull_requests.return_value = [mocker.Mock(), mocker.Mock()]
    response = gs.GithubService(
        domain_gh_conn_settings[0]
    ).merge_pull_request_from_repo(REPO, DOMAIN_MPR)

    assert response == f"{REPO}: unexpected number of PRs for branch:main.\n"
