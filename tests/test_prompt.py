"""Test cases for user prompting module."""
import pytest
from pytest_mock import MockerFixture

import git_portfolio.domain.gh_connection_settings as gcs
import git_portfolio.domain.issue as i
import git_portfolio.domain.pull_request as pr
import git_portfolio.domain.pull_request_merge as prm
import git_portfolio.prompt as p


@pytest.fixture
def mock_inquirer_prompt(mocker: MockerFixture) -> MockerFixture:
    """Fixture for mocking inquirer.prompt."""
    return mocker.patch("inquirer.prompt")


def test_connect_github(mock_inquirer_prompt: MockerFixture) -> None:
    """It returns connection settings."""
    mock_inquirer_prompt.return_value = {
        "github_access_token": "def",
        "github_hostname": "my.host.com",
    }
    expected = gcs.GhConnectionSettings("def", "my.host.com")
    result = p.InquirerPrompter.connect_github("abc")

    assert result == expected


def test_new_repos(mock_inquirer_prompt: MockerFixture) -> None:
    """It returns False."""
    mock_inquirer_prompt.return_value = {"": False}
    result = p.InquirerPrompter.new_repos(["staticdev/omg"])

    assert result is False


def test_select_repos(mock_inquirer_prompt: MockerFixture) -> None:
    """It returns list with repos."""
    mock_inquirer_prompt.side_effect = [
        {"github_repos": []},
        {"github_repos": ["staticdev/omg"]},
    ]
    result = p.InquirerPrompter.select_repos(["staticdev/omg"])

    assert result == ["staticdev/omg"]


def test_create_issues(mock_inquirer_prompt: MockerFixture) -> None:
    """It returns issue."""
    mock_inquirer_prompt.return_value = {
        "title": "my title",
        "labels": "testing,refactor",
        "body": "my body",
        "correct": True,
    }
    result = p.InquirerPrompter.create_issues(["staticdev/omg"])
    expected = i.Issue("my title", "my body", "testing,refactor")

    assert result == expected


def test_create_pull_requests(mock_inquirer_prompt: MockerFixture) -> None:
    """It returns pull request."""
    mock_inquirer_prompt.return_value = {
        "title": "my title",
        "body": "my body",
        "labels": "testing",
        "confirmation": True,
        "link": "issue title",
        "inherit_labels": True,
        "head": "main",
        "base": "branch",
        "draft": True,
        "correct": True,
    }
    result = p.InquirerPrompter.create_pull_requests(["staticdev/omg"])
    expected = pr.PullRequest(
        "my title",
        "my body",
        "testing",
        True,
        "issue title",
        True,
        "main",
        "branch",
        True,
    )

    assert result == expected


def test_delete_branches(mock_inquirer_prompt: MockerFixture) -> None:
    """It returns branch name."""
    mock_inquirer_prompt.return_value = {"branch": "branch name", "correct": True}
    result = p.InquirerPrompter.delete_branches(["staticdev/omg"])
    expected = "branch name"

    assert result == expected


def test_merge_pull_requests(mock_inquirer_prompt: MockerFixture) -> None:
    """It returns pull request merge."""
    mock_inquirer_prompt.return_value = {
        "base": "branch",
        "head": "main",
        "prefix": "org name",
        "delete_branch": True,
        "correct": True,
    }
    result = p.InquirerPrompter.merge_pull_requests("staticdev", ["staticdev/omg"])
    expected = prm.PullRequestMerge("branch", "main", "org name", True)

    assert result == expected
