"""Test cases for the Github service module."""
from __future__ import annotations

import unittest

import github3
import pytest
from pytest_mock import MockerFixture

import git_portfolio.domain.gh_connection_settings as cs
import git_portfolio.domain.issue as i
import git_portfolio.domain.pull_request as pr
import git_portfolio.domain.pull_request_merge as mpr
import git_portfolio.github_service as gs
import git_portfolio.request_objects.issue_list as il


REPO = "org/repo-name"
REPO2 = "org/repo-name2"
INVALID_REQUEST_ISSUES = il.IssueListInvalidRequest()
NO_FILTER_REQUEST_ISSUES = il.IssueListValidRequest()


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
def domain_issues() -> list[i.Issue]:
    """Issues fixture."""
    issues = [
        i.Issue(
            0,
            "my issue title",
            "my issue body",
            {"testing", "refactor"},
        ),
        i.Issue(2, "also doesnt match title", "body2", set()),
        i.Issue(4, "doesnt match title", "body4", {"dontinherit"}),
        i.Issue(3, "issue title", "body3", set()),
        i.Issue(5, "pr match issue title", "body5", {"enhancement", "testing"}),
    ]
    return issues


@pytest.fixture
def domain_prs() -> list[pr.PullRequest]:
    """Pull requests fixture."""
    prs = [
        pr.PullRequest(
            "my pr title",
            "my pr body",
            set(),
            False,
            "",
            False,
            "main",
            "branch",
            False,
        ),
        pr.PullRequest(
            "my pr title 2",
            "my pr body 2",
            {"testing", "refactor"},
            True,
            "issue title",
            True,
            "main",
            "branch",
            False,
        ),
    ]
    return prs


@pytest.fixture
def domain_mpr() -> mpr.PullRequestMerge:
    """Pull request merge fixture."""
    return mpr.PullRequestMerge("branch", "main", "org name", False)


@pytest.fixture
def domain_branch() -> str:
    """Branch fixture."""
    return "my-branch"


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
    with pytest.raises(gs.GithubServiceError) as excinfo:
        gs.GithubService(domain_gh_conn_settings[0])

    assert "Invalid token." == str(excinfo.value)


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
    with pytest.raises(ConnectionError):
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
    domain_issues: list[i.Issue],
) -> None:
    """It succeeds."""
    response = gs.GithubService(domain_gh_conn_settings[0]).create_issue_from_repo(
        REPO, domain_issues[0]
    )

    assert response == f"{REPO}: create issue successful.\n"


def test_create_issue_from_repo_fork(
    mocker: MockerFixture,
    domain_gh_conn_settings: list[cs.GhConnectionSettings],
    mock_github3_login: MockerFixture,
    domain_issues: list[i.Issue],
) -> None:
    """It gives a message error telling it is a fork."""
    exception_mock = mocker.Mock()
    exception_mock.json.return_value.get.return_value = (
        "Issues are disabled for this repo"
    )
    repo = mock_github3_login.return_value.repositories.return_value[1]
    repo.create_issue.side_effect = github3.exceptions.ClientError(exception_mock)
    response = gs.GithubService(domain_gh_conn_settings[0]).create_issue_from_repo(
        REPO, domain_issues[0]
    )

    assert response == f"{REPO}: Issues are disabled for this repo. It may be a fork.\n"


def test_create_issue_from_repo_other_client_error(
    mocker: MockerFixture,
    domain_gh_conn_settings: list[cs.GhConnectionSettings],
    mock_github3_login: MockerFixture,
    domain_issues: list[i.Issue],
) -> None:
    """It gives the message error returned from the API."""
    exception_mock = mocker.Mock()
    exception_mock.json.return_value.get.return_value = "returned message"
    repo = mock_github3_login.return_value.repositories.return_value[1]
    repo.create_issue.side_effect = github3.exceptions.ClientError(exception_mock)
    response = gs.GithubService(domain_gh_conn_settings[0]).create_issue_from_repo(
        REPO, domain_issues[0]
    )

    assert response == f"{REPO}: returned message.\n"


def test_create_issue_from_repo_other_error(
    mocker: MockerFixture,
    domain_gh_conn_settings: list[cs.GhConnectionSettings],
    mock_github3_login: MockerFixture,
    domain_issues: list[i.Issue],
) -> None:
    """It gives the message error returned from the API."""
    exception_mock = mocker.Mock()
    exception_mock.json.return_value.get.return_value = "returned message"
    repo = mock_github3_login.return_value.repositories.return_value[1]
    repo.create_issue.side_effect = github3.exceptions.ForbiddenError(exception_mock)

    with pytest.raises(gs.GithubServiceError, match="org/repo-name: returned message"):
        gs.GithubService(domain_gh_conn_settings[0]).create_issue_from_repo(
            REPO, domain_issues[0]
        )


def test_list_issues_from_repo_title_filter(
    mocker: MockerFixture,
    domain_gh_conn_settings: list[cs.GhConnectionSettings],
    domain_issues: list[i.Issue],
    mock_github3_login: MockerFixture,
) -> None:
    """It succeeds."""
    label1 = mocker.Mock()
    label1.name = "dontinherit"
    label2 = mocker.Mock()
    label2.name = "enhancement"
    label3 = mocker.Mock()
    label3.name = "testing"

    issue1 = mocker.Mock(title="issue title", number=3)
    issue1.labels.return_value = []
    issue2 = mocker.Mock(title="doesnt match title", number=4)
    issue2.labels.return_value = [label1]
    issue3 = mocker.Mock(title="pr match issue title", number=5)
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
    assert response[0].number == domain_issues[3].number
    assert response[0].title == domain_issues[3].title
    assert response[1].number == domain_issues[4].number
    assert response[1].title == domain_issues[4].title


@pytest.mark.parametrize("value", ["issue", "pull request"])
def test_list_issues_from_repo_obj_filter(
    value: str,
    mocker: MockerFixture,
    domain_gh_conn_settings: list[cs.GhConnectionSettings],
    domain_issues: list[i.Issue],
    mock_github3_login: MockerFixture,
) -> None:
    """It succeeds."""
    label1 = mocker.Mock()
    label1.name = "enhancement"
    label2 = mocker.Mock()
    label2.name = "testing"

    issue1 = mocker.Mock(title="issue title", number=3, pull_request_urls=None)
    issue1.labels.return_value = []
    issue2 = mocker.Mock(
        title="pr match issue title", number=5, pull_request_urls="something"
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
        assert response[0].number == domain_issues[3].number
        assert response[0].title == domain_issues[3].title
    elif value == "pr":
        assert response[0].number == domain_issues[4].number
        assert response[0].title == domain_issues[4].title


def test_list_issues_from_repo_invalid_request(
    domain_gh_conn_settings: list[cs.GhConnectionSettings],
    domain_issues: list[i.Issue],
    mock_github3_login: MockerFixture,
) -> None:
    """It returns empty result."""
    response = gs.GithubService(domain_gh_conn_settings[0]).list_issues_from_repo(
        REPO, INVALID_REQUEST_ISSUES
    )

    assert response == []


def test_list_issues_from_repo_no_filter_request(
    mocker: MockerFixture,
    domain_gh_conn_settings: list[cs.GhConnectionSettings],
    domain_issues: list[i.Issue],
    mock_github3_login: MockerFixture,
) -> None:
    """It returns empty result."""
    issue1 = mocker.Mock(title="issue title", number=3)
    issue1.labels.return_value = []
    issue2 = mocker.Mock(title="doesnt match title", number=4)
    issue2.labels.return_value = []
    repo = mock_github3_login.return_value.repositories.return_value[1]
    repo.issues.return_value = [
        issue1,
        issue2,
    ]

    response = gs.GithubService(domain_gh_conn_settings[0]).list_issues_from_repo(
        REPO, NO_FILTER_REQUEST_ISSUES
    )

    assert len(response) == 2
    assert response[0].number == domain_issues[3].number
    assert response[1].number == domain_issues[2].number
    assert response[0].title == domain_issues[3].title
    assert response[1].title == domain_issues[2].title


def test_close_issues_from_repo_success(
    domain_gh_conn_settings: list[cs.GhConnectionSettings],
    domain_issues: list[i.Issue],
    mock_github3_login: MockerFixture,
) -> None:
    """It succeeds."""
    mock_github3_login.return_value.issue().is_closed.return_value = False
    response = gs.GithubService(domain_gh_conn_settings[0]).close_issues_from_repo(
        REPO, domain_issues
    )

    assert response == f"{REPO}: close issues successful.\n"


def test_close_issues_from_repo_no_issue(
    domain_gh_conn_settings: list[cs.GhConnectionSettings],
    domain_issues: list[i.Issue],
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
    domain_issues: list[i.Issue],
    mock_github3_login: MockerFixture,
) -> None:
    """It succeeds."""
    mock_github3_login.return_value.issue().is_closed.return_value = True
    response = gs.GithubService(domain_gh_conn_settings[0]).close_issues_from_repo(
        REPO, domain_issues
    )

    assert response == f"{REPO}: close issues successful.\n"


def test_reopen_issues_from_repo_success(
    domain_gh_conn_settings: list[cs.GhConnectionSettings],
    domain_issues: list[i.Issue],
    mock_github3_login: MockerFixture,
) -> None:
    """It succeeds."""
    response = gs.GithubService(domain_gh_conn_settings[0]).reopen_issues_from_repo(
        REPO, domain_issues
    )

    assert response == f"{REPO}: reopen issues successful.\n"


def test_reopen_issues_from_repo_no_issue(
    domain_gh_conn_settings: list[cs.GhConnectionSettings],
    domain_issues: list[i.Issue],
    mock_github3_login: MockerFixture,
) -> None:
    """It returns a not issue message."""
    response = gs.GithubService(domain_gh_conn_settings[0]).reopen_issues_from_repo(
        REPO, []
    )

    assert response == f"{REPO}: no issues match.\n"


def test_create_pull_request_from_repo_success(
    domain_gh_conn_settings: list[cs.GhConnectionSettings],
    mock_github3_login: MockerFixture,
    domain_prs: list[pr.PullRequest],
) -> None:
    """It succeeds."""
    response = gs.GithubService(
        domain_gh_conn_settings[0]
    ).create_pull_request_from_repo(REPO, domain_prs[0])

    assert response == f"{REPO}: create PR successful.\n"


def test_create_pull_request_from_repo_with_labels(
    domain_gh_conn_settings: list[cs.GhConnectionSettings],
    mock_github3_login: MockerFixture,
    domain_prs: list[pr.PullRequest],
) -> None:
    """It succeeds."""
    response = gs.GithubService(
        domain_gh_conn_settings[0]
    ).create_pull_request_from_repo(REPO, domain_prs[1])

    assert response == f"{REPO}: create PR successful.\n"


# Details on mocking exception constructor at
# stackoverflow.com/questions/64226516/how-to-set-mocked-exception-behavior-on-python
def test_create_pull_request_from_repo_invalid_branch(
    mocker: MockerFixture,
    domain_gh_conn_settings: list[cs.GhConnectionSettings],
    mock_github3_login: MockerFixture,
    domain_prs: list[pr.PullRequest],
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
    ).create_pull_request_from_repo(REPO, domain_prs[1])

    assert response == f"{REPO}: Validation Failed. Invalid field head.\n"


@pytest.mark.e2e
def test_create_pull_request_from_repo_invalid_branch_unpatched_exception(
    mocker: MockerFixture,
    domain_gh_conn_settings: list[cs.GhConnectionSettings],
    mock_github3_login: MockerFixture,
    domain_prs: list[pr.PullRequest],
) -> None:
    """It gives the message error informing the invalid field head."""
    mocked_response = mocker.Mock()
    mocked_response.json.return_value = {
        "message": "Validation Failed",
        "errors": [{"field": "head"}],
    }

    repo = mock_github3_login.return_value.repositories.return_value[1]
    repo.create_pull.side_effect = github3.exceptions.UnprocessableEntity(
        mocked_response
    )
    response = gs.GithubService(
        domain_gh_conn_settings[0]
    ).create_pull_request_from_repo(REPO, domain_prs[1])

    assert response == f"{REPO}: Validation Failed. Invalid field head.\n"


# Details on mocking exception constructor at
# stackoverflow.com/questions/64226516/how-to-set-mocked-exception-behavior-on-python
def test_create_pull_request_from_repo_no_commits(
    mocker: MockerFixture,
    domain_gh_conn_settings: list[cs.GhConnectionSettings],
    mock_github3_login: MockerFixture,
    domain_prs: list[pr.PullRequest],
) -> None:
    """It gives the message error from the exception."""

    def _initiate_mocked_exception(
        self: github3.exceptions.UnprocessableEntity,
    ) -> None:
        self.errors = [{"message": "No commits between main and new-branch"}]
        self.msg = "Validation Failed"

    mocker.patch.object(
        github3.exceptions.UnprocessableEntity, "__init__", _initiate_mocked_exception
    )

    repo = mock_github3_login.return_value.repositories.return_value[1]
    repo.create_pull.side_effect = github3.exceptions.UnprocessableEntity
    response = gs.GithubService(
        domain_gh_conn_settings[0]
    ).create_pull_request_from_repo(REPO, domain_prs[1])

    assert response == (
        f"{REPO}: Validation Failed. No commits between main and " "new-branch.\n"
    )


@pytest.mark.e2e
def test_create_pull_request_from_repo_no_commits_unpatched_exception(
    mocker: MockerFixture,
    domain_gh_conn_settings: list[cs.GhConnectionSettings],
    mock_github3_login: MockerFixture,
    domain_prs: list[pr.PullRequest],
) -> None:
    """It gives the message error from the exception."""
    mocked_response = mocker.Mock()
    mocked_response.json.return_value = {
        "message": "Validation Failed",
        "errors": [{"message": "No commits between main and new-branch"}],
    }

    repo = mock_github3_login.return_value.repositories.return_value[1]
    repo.create_pull.side_effect = github3.exceptions.UnprocessableEntity(
        mocked_response
    )
    response = gs.GithubService(
        domain_gh_conn_settings[0]
    ).create_pull_request_from_repo(REPO, domain_prs[1])

    assert response == (
        f"{REPO}: Validation Failed. No commits between main and " "new-branch.\n"
    )


def test_create_pull_request_from_repo_other_error(
    mocker: MockerFixture,
    domain_gh_conn_settings: list[cs.GhConnectionSettings],
    mock_github3_login: MockerFixture,
    domain_prs: list[pr.PullRequest],
) -> None:
    """It gives the message error returned from the API."""
    exception_mock = mocker.Mock()
    exception_mock.json.return_value.get.return_value = "returned message"
    repo = mock_github3_login.return_value.repositories.return_value[1]
    repo.create_pull.side_effect = github3.exceptions.ForbiddenError(exception_mock)

    with pytest.raises(gs.GithubServiceError, match="org/repo-name: returned message"):
        gs.GithubService(domain_gh_conn_settings[0]).create_pull_request_from_repo(
            REPO, domain_prs[0]
        )


def test_link_issue_success(
    domain_gh_conn_settings: list[cs.GhConnectionSettings],
    domain_issues: list[i.Issue],
    domain_prs: list[pr.PullRequest],
    mock_github3_login: MockerFixture,
) -> None:
    """It succeeds."""
    pr = gs.GithubService(domain_gh_conn_settings[0]).link_issues(
        domain_prs[1], domain_issues[3:]
    )

    assert domain_prs[1].body == "my pr body 2"
    assert pr.body == "my pr body 2\n\nCloses #3\nCloses #5\n"
    case = unittest.TestCase()
    case.assertCountEqual(domain_prs[1].labels, {"testing", "refactor"})
    case.assertCountEqual(pr.labels, {"testing", "refactor", "enhancement"})


def test_link_issue_no_link(
    domain_gh_conn_settings: list[cs.GhConnectionSettings],
    domain_issues: list[i.Issue],
    domain_prs: list[pr.PullRequest],
    mock_github3_login: MockerFixture,
) -> None:
    """It succeeds without any linked issue."""
    gs.GithubService(domain_gh_conn_settings[0]).link_issues(domain_prs[1], [])

    assert domain_prs[1].body == "my pr body 2"


def test_delete_branch_from_repo_success(
    mocker: MockerFixture,
    domain_gh_conn_settings: list[cs.GhConnectionSettings],
    mock_github3_login: MockerFixture,
    domain_branch: str,
) -> None:
    """It succeeds."""
    response = gs.GithubService(domain_gh_conn_settings[0]).delete_branch_from_repo(
        REPO, domain_branch
    )

    assert response == f"{REPO}: delete branch successful.\n"


def test_delete_branch_from_repo_branch_not_found(
    mocker: MockerFixture,
    domain_gh_conn_settings: list[cs.GhConnectionSettings],
    mock_github3_login: MockerFixture,
    domain_branch: str,
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
        REPO, domain_branch
    )

    assert response == f"{REPO}: Not found.\n"


def test_delete_branch_from_repo_other_error(
    mocker: MockerFixture,
    domain_gh_conn_settings: list[cs.GhConnectionSettings],
    mock_github3_login: MockerFixture,
    domain_branch: str,
) -> None:
    """It gives the message error returned from the API."""
    exception_mock = mocker.Mock()
    exception_mock.json.return_value.get.return_value = "returned message"
    repo = mock_github3_login.return_value.repositories.return_value[1]
    repo.ref.side_effect = github3.exceptions.ForbiddenError(exception_mock)

    with pytest.raises(gs.GithubServiceError, match=f"{REPO}: returned message"):
        gs.GithubService(domain_gh_conn_settings[0]).delete_branch_from_repo(
            REPO, domain_branch
        )


def test_merge_pull_request_from_repo_success(
    mocker: MockerFixture,
    domain_gh_conn_settings: list[cs.GhConnectionSettings],
    mock_github3_login: MockerFixture,
    domain_mpr: mpr.PullRequestMerge,
) -> None:
    """It succeeds."""
    repo = mock_github3_login.return_value.repositories.return_value[1]
    repo.pull_requests.return_value = [mocker.Mock()]
    response = gs.GithubService(
        domain_gh_conn_settings[0]
    ).merge_pull_request_from_repo(REPO, domain_mpr)

    assert response == f"{REPO}: merge PR successful.\n"


def test_merge_pull_request_from_repo_error_merging(
    mocker: MockerFixture,
    domain_gh_conn_settings: list[cs.GhConnectionSettings],
    mock_github3_login: MockerFixture,
    domain_mpr: mpr.PullRequestMerge,
) -> None:
    """It throws exception."""
    repo = mock_github3_login.return_value.repositories.return_value[1]
    pr = mocker.Mock()
    pr.merge.side_effect = github3.exceptions.MethodNotAllowed(mocker.Mock())
    repo.pull_requests.return_value = [pr]
    with pytest.raises(gs.GithubServiceError):
        gs.GithubService(domain_gh_conn_settings[0]).merge_pull_request_from_repo(
            REPO, domain_mpr
        )


def test_merge_pull_request_from_repo_not_found(
    domain_gh_conn_settings: list[cs.GhConnectionSettings],
    mock_github3_login: MockerFixture,
    domain_mpr: mpr.PullRequestMerge,
) -> None:
    """It gives error message."""
    repo = mock_github3_login.return_value.repositories.return_value[1]
    repo.pull_requests.return_value = []
    response = gs.GithubService(
        domain_gh_conn_settings[0]
    ).merge_pull_request_from_repo(REPO, domain_mpr)

    assert response == f"{REPO}: no open PR found for branch:main.\n"


def test_merge_pull_request_from_repo_ambiguous(
    mocker: MockerFixture,
    domain_gh_conn_settings: list[cs.GhConnectionSettings],
    mock_github3_login: MockerFixture,
    domain_mpr: mpr.PullRequestMerge,
) -> None:
    """It gives error message."""
    repo = mock_github3_login.return_value.repositories.return_value[1]
    repo.pull_requests.return_value = [mocker.Mock(), mocker.Mock()]
    response = gs.GithubService(
        domain_gh_conn_settings[0]
    ).merge_pull_request_from_repo(REPO, domain_mpr)

    assert response == f"{REPO}: unexpected number of PRs for branch:main.\n"
