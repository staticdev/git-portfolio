"""Test cases for the Github service module."""
import unittest
from typing import List

import github3
import pytest
from pytest_mock import MockerFixture

import git_portfolio.domain.gh_connection_settings as cs
import git_portfolio.domain.issue as i
import git_portfolio.domain.pull_request as pr
import git_portfolio.domain.pull_request_merge as mpr
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
def domain_prs() -> List[pr.PullRequest]:
    """Pull requests fixture."""
    prs = [
        pr.PullRequest(
            "my title",
            "my body",
            set(),
            False,
            "",
            False,
            "main",
            "branch",
            False,
        ),
        pr.PullRequest(
            "my title",
            "my body",
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
    mock = mocker.patch("github3.login", autospec=True)
    mock.return_value.repositories.return_value = [
        mocker.Mock(full_name="staticdev/nope"),
        mocker.Mock(full_name="staticdev/omg"),
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


def test_init_invalid_token(
    mocker: MockerFixture,
    domain_gh_conn_settings: List[cs.GhConnectionSettings],
    mock_github3_login: MockerFixture,
) -> None:
    """It returns invalid token message."""
    mock_github3_login.return_value.me.side_effect = (
        github3.exceptions.AuthenticationFailed(mocker.Mock())
    )
    with pytest.raises(AttributeError) as excinfo:
        gc.GithubService(domain_gh_conn_settings[0])

    assert "Invalid token." == str(excinfo.value)


def test_init_invalid_token_scope(
    mocker: MockerFixture,
    domain_gh_conn_settings: List[cs.GhConnectionSettings],
    mock_github3_login: MockerFixture,
) -> None:
    """It returns invalid response message."""
    mock_github3_login.return_value.me.side_effect = (
        github3.exceptions.IncompleteResponse(mocker.Mock(), mocker.Mock())
    )
    with pytest.raises(AttributeError) as excinfo:
        gc.GithubService(domain_gh_conn_settings[0])

    assert "Invalid response. Your token might not be properly scoped." == str(
        excinfo.value
    )


def test_init_connection_error(
    mocker: MockerFixture,
    domain_gh_conn_settings: List[cs.GhConnectionSettings],
    mock_github3_login: MockerFixture,
) -> None:
    """It succeeds."""
    mock_github3_login.return_value.me.side_effect = github3.exceptions.ConnectionError(
        mocker.Mock()
    )
    with pytest.raises(ConnectionError):
        gc.GithubService(domain_gh_conn_settings[0])


def test_get_repo_no_repo(
    mocker: MockerFixture, domain_gh_conn_settings: List[cs.GhConnectionSettings]
) -> None:
    """It returns None."""
    mock = mocker.patch("github3.login", autospec=True)
    mock.return_value.repositories.return_value = []

    with pytest.raises(NameError):
        gc.GithubService(domain_gh_conn_settings[0])._get_repo("staticdev/omg")


def test_get_repo_names(
    domain_gh_conn_settings: List[cs.GhConnectionSettings],
    mock_github3_login: MockerFixture,
) -> None:
    """It returns list of strings."""
    expected = ["staticdev/nope", "staticdev/omg"]
    result = gc.GithubService(domain_gh_conn_settings[0]).get_repo_names()

    assert result == expected


def test_get_username(
    domain_gh_conn_settings: List[cs.GhConnectionSettings],
    mock_github3_login: MockerFixture,
) -> None:
    """It returns user name."""
    expected = "staticdev"
    mock_github3_login.return_value.me.return_value.login = "staticdev"
    result = gc.GithubService(domain_gh_conn_settings[0]).get_username()

    assert result == expected


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
    mocker: MockerFixture,
    domain_gh_conn_settings: List[cs.GhConnectionSettings],
    mock_github3_login: MockerFixture,
    domain_issue: i.Issue,
) -> None:
    """It gives a message error telling it is a fork."""
    exception_mock = mocker.Mock()
    exception_mock.json.return_value.get.return_value = (
        "Issues are disabled for this repo"
    )
    repo = mock_github3_login.return_value.repositories.return_value[1]
    repo.create_issue.side_effect = github3.exceptions.ClientError(exception_mock)
    response = gc.GithubService(domain_gh_conn_settings[0]).create_issue_from_repo(
        "staticdev/omg", domain_issue
    )

    assert (
        response
        == "staticdev/omg: Issues are disabled for this repo. It may be a fork."
    )


def test_create_issue_from_repo_other_error(
    mocker: MockerFixture,
    domain_gh_conn_settings: List[cs.GhConnectionSettings],
    mock_github3_login: MockerFixture,
    domain_issue: i.Issue,
) -> None:
    """It gives the message error returned from the API."""
    exception_mock = mocker.Mock()
    exception_mock.json.return_value.get.return_value = "returned message"
    repo = mock_github3_login.return_value.repositories.return_value[1]
    repo.create_issue.side_effect = github3.exceptions.ClientError(exception_mock)
    response = gc.GithubService(domain_gh_conn_settings[0]).create_issue_from_repo(
        "staticdev/omg", domain_issue
    )

    assert response == "staticdev/omg: returned message."


def test_create_pull_request_from_repo_success(
    domain_gh_conn_settings: List[cs.GhConnectionSettings],
    mock_github3_login: MockerFixture,
    domain_prs: List[pr.PullRequest],
) -> None:
    """It succeeds."""
    response = gc.GithubService(
        domain_gh_conn_settings[0]
    ).create_pull_request_from_repo("staticdev/omg", domain_prs[0])

    assert response == "staticdev/omg: PR created successfully."


def test_create_pull_request_from_repo_with_labels(
    domain_gh_conn_settings: List[cs.GhConnectionSettings],
    mock_github3_login: MockerFixture,
    domain_prs: List[pr.PullRequest],
) -> None:
    """It succeeds."""
    response = gc.GithubService(
        domain_gh_conn_settings[0]
    ).create_pull_request_from_repo("staticdev/omg", domain_prs[1])

    assert response == "staticdev/omg: PR created successfully."


# Details on mocking exception constructor at
# stackoverflow.com/questions/64226516/how-to-set-mocked-exception-behavior-on-python
def test_create_pull_request_from_repo_invalid_branch(
    mocker: MockerFixture,
    domain_gh_conn_settings: List[cs.GhConnectionSettings],
    mock_github3_login: MockerFixture,
    domain_prs: List[pr.PullRequest],
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
    response = gc.GithubService(
        domain_gh_conn_settings[0]
    ).create_pull_request_from_repo("staticdev/omg", domain_prs[1])

    assert response == "staticdev/omg: Validation Failed. Invalid field head."


@pytest.mark.e2e
def test_create_pull_request_from_repo_invalid_branch_unpatched_exception(
    mocker: MockerFixture,
    domain_gh_conn_settings: List[cs.GhConnectionSettings],
    mock_github3_login: MockerFixture,
    domain_prs: List[pr.PullRequest],
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
    response = gc.GithubService(
        domain_gh_conn_settings[0]
    ).create_pull_request_from_repo("staticdev/omg", domain_prs[1])

    assert response == "staticdev/omg: Validation Failed. Invalid field head."


# Details on mocking exception constructor at
# stackoverflow.com/questions/64226516/how-to-set-mocked-exception-behavior-on-python
def test_create_pull_request_from_repo_no_commits(
    mocker: MockerFixture,
    domain_gh_conn_settings: List[cs.GhConnectionSettings],
    mock_github3_login: MockerFixture,
    domain_prs: List[pr.PullRequest],
) -> None:
    """It gives the message error from the exception."""

    def _initiate_mocked_exception(
        self: github3.exceptions.UnprocessableEntity,
    ) -> None:
        self.errors = [{"message": "No commits between master and new-branch"}]
        self.msg = "Validation Failed"

    mocker.patch.object(
        github3.exceptions.UnprocessableEntity, "__init__", _initiate_mocked_exception
    )

    repo = mock_github3_login.return_value.repositories.return_value[1]
    repo.create_pull.side_effect = github3.exceptions.UnprocessableEntity
    response = gc.GithubService(
        domain_gh_conn_settings[0]
    ).create_pull_request_from_repo("staticdev/omg", domain_prs[1])

    assert (
        response
        == "staticdev/omg: Validation Failed. No commits between master and new-branch."
    )


@pytest.mark.e2e
def test_create_pull_request_from_repo_no_commits_unpatched_exception(
    mocker: MockerFixture,
    domain_gh_conn_settings: List[cs.GhConnectionSettings],
    mock_github3_login: MockerFixture,
    domain_prs: List[pr.PullRequest],
) -> None:
    """It gives the message error from the exception."""
    mocked_response = mocker.Mock()
    mocked_response.json.return_value = {
        "message": "Validation Failed",
        "errors": [{"message": "No commits between master and new-branch"}],
    }

    repo = mock_github3_login.return_value.repositories.return_value[1]
    repo.create_pull.side_effect = github3.exceptions.UnprocessableEntity(
        mocked_response
    )
    response = gc.GithubService(
        domain_gh_conn_settings[0]
    ).create_pull_request_from_repo("staticdev/omg", domain_prs[1])

    assert (
        response
        == "staticdev/omg: Validation Failed. No commits between master and new-branch."
    )


def test_link_issue_success(
    mocker: MockerFixture,
    domain_gh_conn_settings: List[cs.GhConnectionSettings],
    mock_github3_login: MockerFixture,
    domain_prs: List[pr.PullRequest],
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
    issue3 = mocker.Mock(title="match issue title", number=5)
    issue3.labels.return_value = [label2, label3]

    repo = mock_github3_login.return_value.repositories.return_value[1]
    repo.issues.return_value = [
        issue1,
        issue2,
        issue3,
    ]
    gc.GithubService(domain_gh_conn_settings[0]).link_issues(
        "staticdev/omg", domain_prs[1]
    )

    assert domain_prs[1].body == "my body\n\nCloses #3\nCloses #5\n"
    case = unittest.TestCase()
    case.assertCountEqual(domain_prs[1].labels, {"testing", "refactor", "enhancement"})


def test_link_issue_no_link(
    mocker: MockerFixture,
    domain_gh_conn_settings: List[cs.GhConnectionSettings],
    mock_github3_login: MockerFixture,
    domain_prs: List[pr.PullRequest],
) -> None:
    """It succeeds without any linked issue."""
    issue1 = mocker.Mock(title="doesnt match title", number=1)
    issue2 = mocker.Mock(title="also doesnt match title", number=2)

    repo = mock_github3_login.return_value.repositories.return_value[1]
    repo.issues.return_value = [
        issue1,
        issue2,
    ]
    gc.GithubService(domain_gh_conn_settings[0]).link_issues(
        "staticdev/omg", domain_prs[1]
    )

    assert domain_prs[1].body == "my body"


def test_delete_branch_from_repo_success(
    mocker: MockerFixture,
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
    mocker: MockerFixture,
    domain_gh_conn_settings: List[cs.GhConnectionSettings],
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

    response = gc.GithubService(domain_gh_conn_settings[0]).delete_branch_from_repo(
        "staticdev/omg", domain_branch
    )

    assert response == "staticdev/omg: Not found."


def test_merge_pull_request_from_repo_success(
    mocker: MockerFixture,
    domain_gh_conn_settings: List[cs.GhConnectionSettings],
    mock_github3_login: MockerFixture,
    domain_mpr: mpr.PullRequestMerge,
) -> None:
    """It succeeds."""
    repo = mock_github3_login.return_value.repositories.return_value[1]
    repo.pull_requests.return_value = [mocker.Mock()]
    response = gc.GithubService(
        domain_gh_conn_settings[0]
    ).merge_pull_request_from_repo("staticdev/omg", domain_mpr)

    assert response == "staticdev/omg: PR merged successfully."


def test_merge_pull_request_from_repo_error_merging() -> None:
    """It gives error message."""
    pass


def test_merge_pull_request_from_repo_not_found(
    domain_gh_conn_settings: List[cs.GhConnectionSettings],
    mock_github3_login: MockerFixture,
    domain_mpr: mpr.PullRequestMerge,
) -> None:
    """It gives error message."""
    repo = mock_github3_login.return_value.repositories.return_value[1]
    repo.pull_requests.return_value = []
    response = gc.GithubService(
        domain_gh_conn_settings[0]
    ).merge_pull_request_from_repo("staticdev/omg", domain_mpr)

    assert response == "staticdev/omg: no open PR found for branch:main."


def test_merge_pull_request_from_repo_ambiguous(
    mocker: MockerFixture,
    domain_gh_conn_settings: List[cs.GhConnectionSettings],
    mock_github3_login: MockerFixture,
    domain_mpr: mpr.PullRequestMerge,
) -> None:
    """It gives error message."""
    repo = mock_github3_login.return_value.repositories.return_value[1]
    repo.pull_requests.return_value = [mocker.Mock(), mocker.Mock()]
    response = gc.GithubService(
        domain_gh_conn_settings[0]
    ).merge_pull_request_from_repo("staticdev/omg", domain_mpr)

    assert response == "staticdev/omg: unexpected number of PRs for branch:main."
