"""Test cases for the __main__ module."""
from unittest.mock import Mock
from unittest.mock import patch

import pytest
from click.testing import CliRunner
from pytest_mock import MockerFixture

import git_portfolio.__main__
import git_portfolio.response_objects as res


@pytest.fixture
def runner() -> CliRunner:
    """Fixture for invoking command-line interfaces."""
    return CliRunner()


@pytest.fixture
def mock_config_manager(mocker: MockerFixture) -> MockerFixture:
    """Fixture for mocking CONFIG_MANAGER."""
    return mocker.patch("git_portfolio.__main__.CONFIG_MANAGER")


@pytest.fixture
def mock_github_manager(mocker: MockerFixture) -> MockerFixture:
    """Fixture for mocking GithubManager."""
    return mocker.patch("git_portfolio.github_manager.GithubManager", autospec=True)


@pytest.fixture
def mock_git_use_case(mocker: MockerFixture) -> MockerFixture:
    """Fixture for mocking GitUseCase."""
    return mocker.patch(
        "git_portfolio.use_cases.git_use_case.GitUseCase", autospec=True
    )


def test_git_command_success(
    mock_config_manager: MockerFixture, runner: CliRunner
) -> None:
    """It outputs success message."""
    mock_config_manager.config.github_selected_repos = ["staticdev/omg"]

    @git_portfolio.__main__.main.command("test")
    @git_portfolio.__main__.git_command
    def _() -> res.ResponseSuccess:
        return res.ResponseSuccess("success message")

    result = runner.invoke(git_portfolio.__main__.main, ["test"], prog_name="gitp")

    assert "success message" in result.output


def test_git_command_execute_error(
    mock_config_manager: MockerFixture, runner: CliRunner
) -> None:
    """It calls a command an error response."""
    mock_config_manager.config.github_selected_repos = ["staticdev/omg"]

    @git_portfolio.__main__.main.command("test")
    @git_portfolio.__main__.git_command
    def _() -> res.ResponseFailure:
        return res.ResponseFailure.build_system_error("some error msg")

    result = runner.invoke(git_portfolio.__main__.main, ["test"], prog_name="gitp")

    assert "Error: some error msg" in result.output


def test_git_command_no_repos(mock_config_manager: Mock, runner: CliRunner) -> None:
    """It outputs no repos selected error message."""

    @git_portfolio.__main__.main.command("test")
    @git_portfolio.__main__.git_command
    def _() -> res.ResponseFailure:
        return res.ResponseFailure.build_system_error("some error msg")

    mock_config_manager.config.github_selected_repos = []
    result = runner.invoke(git_portfolio.__main__.main, ["test"], prog_name="gitp")

    assert result.output.startswith("Error: no repos selected.")


def test_checkout_success(
    mock_git_use_case: MockerFixture, mock_config_manager: Mock, runner: CliRunner
) -> None:
    """It calls checkout with master."""
    mock_config_manager.config.github_selected_repos = ["staticdev/omg"]
    runner.invoke(git_portfolio.__main__.main, ["checkout", "master"], prog_name="gitp")

    mock_git_use_case.return_value.execute.assert_called_once_with(
        ["staticdev/omg"], "checkout", ("master",)
    )


def test_commit_success(
    mock_git_use_case: MockerFixture, mock_config_manager: Mock, runner: CliRunner
) -> None:
    """It calls commit with message."""
    mock_config_manager.config.github_selected_repos = ["staticdev/omg"]
    runner.invoke(
        git_portfolio.__main__.main, ["commit", "-m", "message"], prog_name="gitp"
    )

    mock_git_use_case.return_value.execute.assert_called_once_with(
        ["staticdev/omg"], "commit", ("-m", "message")
    )


def test_pull_success(
    mock_git_use_case: MockerFixture, mock_config_manager: Mock, runner: CliRunner
) -> None:
    """It calls pull."""
    mock_config_manager.config.github_selected_repos = ["staticdev/omg"]
    runner.invoke(git_portfolio.__main__.main, ["pull"], prog_name="gitp")

    mock_git_use_case.return_value.execute.assert_called_once_with(
        ["staticdev/omg"], "pull", ()
    )


def test_push_success(
    mock_git_use_case: MockerFixture, mock_config_manager: Mock, runner: CliRunner
) -> None:
    """It calls push with origin master."""
    mock_config_manager.config.github_selected_repos = ["staticdev/omg"]
    runner.invoke(
        git_portfolio.__main__.main, ["push", "origin", "master"], prog_name="gitp"
    )

    mock_git_use_case.return_value.execute.assert_called_once_with(
        ["staticdev/omg"], "push", ("origin", "master")
    )


def test_push_with_extra_arguments(
    mock_git_use_case: MockerFixture, mock_config_manager: Mock, runner: CliRunner
) -> None:
    """It calls push with --set-upstream origin new-branch."""
    mock_config_manager.config.github_selected_repos = ["staticdev/omg"]
    runner.invoke(
        git_portfolio.__main__.main,
        ["push", "--set-upstream", "origin", "new-branch"],
        prog_name="gitp",
    )

    mock_git_use_case.return_value.execute.assert_called_once_with(
        ["staticdev/omg"], "push", ("--set-upstream", "origin", "new-branch")
    )


def test_status_success(
    mock_git_use_case: MockerFixture, mock_config_manager: Mock, runner: CliRunner
) -> None:
    """It calls status."""
    mock_config_manager.config.github_selected_repos = ["staticdev/omg"]
    runner.invoke(git_portfolio.__main__.main, ["status"], prog_name="gitp")

    mock_git_use_case.return_value.execute.assert_called_once_with(
        ["staticdev/omg"], "status", ()
    )


def test_config_init(
    mock_github_manager: Mock, mock_config_manager: Mock, runner: CliRunner
) -> None:
    """It creates pm.GithubManager."""
    runner.invoke(git_portfolio.__main__.configure, ["init"], prog_name="gitp")

    mock_github_manager.assert_called_once()


def test_config_repos_success(
    mock_github_manager: Mock, mock_config_manager: Mock, runner: CliRunner
) -> None:
    """It call config_repos from pm.GithubManager."""
    mock_config_manager.config_is_empty.return_value = False
    result = runner.invoke(
        git_portfolio.__main__.configure, ["repos"], prog_name="gitp"
    )
    mock_github_manager.assert_called_once()
    mock_github_manager.return_value.config_repos.assert_called_once()
    assert result.output == "gitp successfully configured.\n"


def test_config_repos_do_not_change(
    mock_github_manager: Mock, mock_config_manager: Mock, runner: CliRunner
) -> None:
    """It does not change config file."""
    mock_config_manager.config_is_empty.return_value = False
    mock_github_manager.return_value.config_repos.return_value = None
    result = runner.invoke(
        git_portfolio.__main__.configure, ["repos"], prog_name="gitp"
    )
    mock_github_manager.assert_called_once()
    mock_github_manager.return_value.config_repos.assert_called_once()
    assert "gitp successfully configured.\n" not in result.output


def test_config_repos_no_config(
    mock_github_manager: Mock, mock_config_manager: Mock, runner: CliRunner
) -> None:
    """It returns error message."""
    mock_github_manager.return_value.config_repos.return_value = None
    result = runner.invoke(
        git_portfolio.__main__.configure, ["repos"], prog_name="gitp"
    )
    assert "Error" in result.output


@patch(
    "git_portfolio.use_cases.gh_create_issue_use_case.GhCreateIssueUseCase",
    autospec=True,
)
def test_create_issues(
    mock_gh_create_issue_use_case: Mock,
    mock_github_manager: MockerFixture,
    mock_config_manager: MockerFixture,
    runner: CliRunner,
) -> None:
    """It executes gh_create_issue_use_case."""
    runner.invoke(git_portfolio.__main__.create, ["issues"], prog_name="gitp")
    manager = mock_github_manager.return_value

    mock_gh_create_issue_use_case(manager).execute.assert_called_once()


@patch(
    "git_portfolio.use_cases.gh_create_pr_use_case.GhCreatePrUseCase",
    autospec=True,
)
def test_create_prs(
    mock_gh_create_pr_use_case: Mock,
    mock_github_manager: MockerFixture,
    mock_config_manager: MockerFixture,
    runner: CliRunner,
) -> None:
    """It executes gh_create_pr_use_case."""
    runner.invoke(git_portfolio.__main__.create, ["prs"], prog_name="gitp")
    manager = mock_github_manager.return_value

    mock_gh_create_pr_use_case(manager).execute.assert_called_once()


@patch(
    "git_portfolio.use_cases.gh_merge_pr_use_case.GhMergePrUseCase",
    autospec=True,
)
def test_merge_prs(
    mock_gh_merge_pr_use_case: Mock,
    mock_github_manager: MockerFixture,
    mock_config_manager: MockerFixture,
    runner: CliRunner,
) -> None:
    """It executes gh_merge_pr_use_case."""
    runner.invoke(git_portfolio.__main__.merge, ["prs"], prog_name="gitp")
    manager = mock_github_manager.return_value

    mock_gh_merge_pr_use_case(manager).execute.assert_called_once()


@patch(
    "git_portfolio.use_cases.gh_delete_branch_use_case.GhDeleteBranchUseCase",
    autospec=True,
)
def test_delete_branches(
    mock_gh_delete_branch_use_case: Mock,
    mock_github_manager: MockerFixture,
    mock_config_manager: MockerFixture,
    runner: CliRunner,
) -> None:
    """It call delete_branches from pm.GithubManager."""
    runner.invoke(git_portfolio.__main__.delete, ["branches"], prog_name="gitp")
    manager = mock_github_manager.return_value

    mock_gh_delete_branch_use_case(manager).execute.assert_called_once()
