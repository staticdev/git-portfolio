"""Test cases for the __main__ module."""
from unittest.mock import Mock
from unittest.mock import patch

import pytest
from click.testing import CliRunner

import git_portfolio.__main__
import git_portfolio.response_objects as res


@pytest.fixture
def runner() -> CliRunner:
    """Fixture for invoking command-line interfaces."""
    return CliRunner()


@patch("git_portfolio.__main__.CONFIG_MANAGER")
def test_git_command_success(mock_configmanager: Mock, runner: CliRunner) -> None:
    """It outputs success message."""
    mock_configmanager.config.github_selected_repos = ["staticdev/omg"]

    @git_portfolio.__main__.main.command("test")
    @git_portfolio.__main__.git_command
    def _() -> res.ResponseSuccess:
        return res.ResponseSuccess("success message")

    result = runner.invoke(git_portfolio.__main__.main, ["test"], prog_name="gitp")

    assert "success message" in result.output


@patch("git_portfolio.__main__.CONFIG_MANAGER")
def test_git_command_execute_error(mock_configmanager: Mock, runner: CliRunner) -> None:
    """It calls a command an error response."""
    mock_configmanager.config.github_selected_repos = ["staticdev/omg"]

    @git_portfolio.__main__.main.command("test")
    @git_portfolio.__main__.git_command
    def _() -> res.ResponseFailure:
        return res.ResponseFailure.build_system_error("some error msg")

    result = runner.invoke(git_portfolio.__main__.main, ["test"], prog_name="gitp")

    assert "Error: some error msg" in result.output


@patch("git_portfolio.__main__.CONFIG_MANAGER")
def test_git_command_no_repos(mock_configmanager: Mock, runner: CliRunner) -> None:
    """It outputs no repos selected error message."""

    @git_portfolio.__main__.main.command("test")
    @git_portfolio.__main__.git_command
    def _() -> res.ResponseFailure:
        return res.ResponseFailure.build_system_error("some error msg")

    mock_configmanager.config.github_selected_repos = []
    result = runner.invoke(git_portfolio.__main__.main, ["test"], prog_name="gitp")

    assert result.output.startswith("Error: no repos selected.")


@patch("git_portfolio.__main__.CONFIG_MANAGER")
@patch("git_portfolio.git_use_case.GitUseCase", autospec=True)
def test_checkout_success(
    mock_git_use_case: Mock, mock_configmanager: Mock, runner: CliRunner
) -> None:
    """It calls checkout with master."""
    mock_configmanager.config.github_selected_repos = ["staticdev/omg"]
    runner.invoke(git_portfolio.__main__.main, ["checkout", "master"], prog_name="gitp")

    mock_git_use_case.return_value.execute.assert_called_once_with(
        ["staticdev/omg"], "checkout", ("master",)
    )


@patch("git_portfolio.__main__.CONFIG_MANAGER")
@patch("git_portfolio.git_use_case.GitUseCase", autospec=True)
def test_pull_success(
    mock_git_use_case: Mock, mock_configmanager: Mock, runner: CliRunner
) -> None:
    """It calls pull."""
    mock_configmanager.config.github_selected_repos = ["staticdev/omg"]
    runner.invoke(git_portfolio.__main__.main, ["pull"], prog_name="gitp")

    mock_git_use_case.return_value.execute.assert_called_once_with(
        ["staticdev/omg"], "pull", ()
    )


@patch("git_portfolio.__main__.CONFIG_MANAGER")
@patch("git_portfolio.git_use_case.GitUseCase", autospec=True)
def test_push_success(
    mock_git_use_case: Mock, mock_configmanager: Mock, runner: CliRunner
) -> None:
    """It calls push with origin master."""
    mock_configmanager.config.github_selected_repos = ["staticdev/omg"]
    runner.invoke(
        git_portfolio.__main__.main, ["push", "origin", "master"], prog_name="gitp"
    )

    mock_git_use_case.return_value.execute.assert_called_once_with(
        ["staticdev/omg"], "push", ("origin", "master")
    )


@patch("git_portfolio.__main__.CONFIG_MANAGER")
@patch("git_portfolio.git_use_case.GitUseCase", autospec=True)
def test_status_success(
    mock_git_use_case: Mock, mock_configmanager: Mock, runner: CliRunner
) -> None:
    """It calls status."""
    mock_configmanager.config.github_selected_repos = ["staticdev/omg"]
    runner.invoke(git_portfolio.__main__.main, ["status"], prog_name="gitp")

    mock_git_use_case.return_value.execute.assert_called_once_with(
        ["staticdev/omg"], "status", ()
    )


@patch("git_portfolio.__main__.CONFIG_MANAGER")
@patch("git_portfolio.github_manager.GithubManager", autospec=True)
def test_config_init(
    mock_github_manager: Mock, mock_configmanager: Mock, runner: CliRunner
) -> None:
    """It creates pm.GithubManager."""
    runner.invoke(git_portfolio.__main__.configure, ["init"], prog_name="gitp")

    mock_github_manager.assert_called_once()


@patch("git_portfolio.__main__.CONFIG_MANAGER", autospec=True)
@patch("git_portfolio.github_manager.GithubManager", autospec=True)
def test_config_repos_success(
    mock_github_manager: Mock, mock_configmanager: Mock, runner: CliRunner
) -> None:
    """It call config_repos from pm.GithubManager."""
    mock_configmanager.config_is_empty.return_value = False
    result = runner.invoke(
        git_portfolio.__main__.configure, ["repos"], prog_name="gitp"
    )
    mock_github_manager.assert_called_once()
    mock_github_manager.return_value.config_repos.assert_called_once()
    assert result.output == "gitp successfully configured.\n"


@patch("git_portfolio.__main__.CONFIG_MANAGER", autospec=True)
@patch("git_portfolio.github_manager.GithubManager", autospec=True)
def test_config_repos_do_not_change(
    mock_github_manager: Mock, mock_configmanager: Mock, runner: CliRunner
) -> None:
    """It does not change config file."""
    mock_configmanager.config_is_empty.return_value = False
    mock_github_manager.return_value.config_repos.return_value = None
    result = runner.invoke(
        git_portfolio.__main__.configure, ["repos"], prog_name="gitp"
    )
    mock_github_manager.assert_called_once()
    mock_github_manager.return_value.config_repos.assert_called_once()
    assert "gitp successfully configured.\n" not in result.output


@patch("git_portfolio.__main__.CONFIG_MANAGER")
@patch("git_portfolio.github_manager.GithubManager", autospec=True)
def test_config_repos_no_config(
    mock_github_manager: Mock, mock_configmanager: Mock, runner: CliRunner
) -> None:
    """It returns error message."""
    mock_github_manager.return_value.config_repos.return_value = None
    result = runner.invoke(
        git_portfolio.__main__.configure, ["repos"], prog_name="gitp"
    )
    assert "Error" in result.output


@patch("git_portfolio.github_manager.GithubManager", autospec=True)
def test_create_issues(mock_github_manager: Mock, runner: CliRunner) -> None:
    """It call create_issues from pm.GithubManager."""
    runner.invoke(git_portfolio.__main__.create, ["issues"], prog_name="gitp")
    mock_github_manager.assert_called_once()
    mock_github_manager.return_value.create_issues.assert_called_once()


@patch("git_portfolio.github_manager.GithubManager", autospec=True)
def test_create_prs(mock_github_manager: Mock, runner: CliRunner) -> None:
    """It call create_pull_requests from pm.GithubManager."""
    runner.invoke(git_portfolio.__main__.create, ["prs"], prog_name="gitp")
    mock_github_manager.assert_called_once()
    mock_github_manager.return_value.create_pull_requests.assert_called_once()


@patch("git_portfolio.github_manager.GithubManager", autospec=True)
def test_merge_prs(mock_github_manager: Mock, runner: CliRunner) -> None:
    """It call merge_pull_requests from pm.GithubManager."""
    runner.invoke(git_portfolio.__main__.merge, ["prs"], prog_name="gitp")
    mock_github_manager.assert_called_once()
    mock_github_manager.return_value.merge_pull_requests.assert_called_once()


@patch("git_portfolio.github_manager.GithubManager", autospec=True)
def test_delete_branches(mock_github_manager: Mock, runner: CliRunner) -> None:
    """It call delete_branches from pm.GithubManager."""
    runner.invoke(git_portfolio.__main__.delete, ["branches"], prog_name="gitp")
    mock_github_manager.assert_called_once()
    mock_github_manager.return_value.delete_branches.assert_called_once()
