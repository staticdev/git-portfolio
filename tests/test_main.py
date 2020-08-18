"""Test cases for the __main__ module."""
from unittest.mock import Mock
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from git_portfolio import __main__


@pytest.fixture
def runner() -> CliRunner:
    """Fixture for invoking command-line interfaces."""
    return CliRunner()


@patch("git_portfolio.config_manager.ConfigManager", autospec=True)
@patch("git_portfolio.local_manager.LocalManager", autospec=True)
def test_checkout_success(
    mock_lm_localmanager: Mock, mock_cm_configmanager: Mock, runner: CliRunner
) -> None:
    """It calls checkout with master."""
    mock_cm_configmanager.return_value.load_configs.return_value = Mock(
        github_selected_repos=["staticdev/omg"]
    )
    runner.invoke(__main__.main, ["checkout", "master"], prog_name="gitp")
    mock_lm_localmanager.return_value.checkout.assert_called_once_with(
        ["staticdev/omg"], ("master",)
    )


@patch("git_portfolio.config_manager.ConfigManager", autospec=True)
def test_checkout_no_repos(mock_cm_configmanager: Mock, runner: CliRunner) -> None:
    """It calls checkout with master."""
    mock_cm_configmanager.return_value.load_configs.return_value = Mock(
        github_selected_repos=[]
    )
    result = runner.invoke(__main__.main, ["checkout", "master"], prog_name="gitp")
    assert result.output.startswith("Error: no repos selected.")


@patch("git_portfolio.config_manager.ConfigManager", autospec=True)
@patch("git_portfolio.local_manager.LocalManager", autospec=True)
def test_checkout_two_arguments(
    mock_lm_localmanager: Mock, mock_cm_configmanager: Mock, runner: CliRunner
) -> None:
    """It outputs error."""
    result = runner.invoke(
        __main__.main, ["checkout", "master", "master"], prog_name="gitp"
    )
    assert "Error" in result.output


@patch("git_portfolio.portfolio_manager.PortfolioManager", autospec=True)
def test_config_init(mock_pm_portfoliomanager: Mock, runner: CliRunner) -> None:
    """It creates pm.PortfolioManager."""
    runner.invoke(__main__.configure, ["init"], prog_name="gitp")
    mock_pm_portfoliomanager.assert_called_once()


@patch("git_portfolio.portfolio_manager.PortfolioManager", autospec=True)
def test_config_repos(mock_pm_portfoliomanager: Mock, runner: CliRunner) -> None:
    """It call config_repos from pm.PortfolioManager."""
    runner.invoke(__main__.configure, ["repos"], prog_name="gitp")
    mock_pm_portfoliomanager.assert_called_once()
    mock_pm_portfoliomanager.return_value.config_repos.assert_called_once()


@patch("git_portfolio.portfolio_manager.PortfolioManager", autospec=True)
def test_create_issues(mock_pm_portfoliomanager: Mock, runner: CliRunner) -> None:
    """It call create_issues from pm.PortfolioManager."""
    runner.invoke(__main__.create, ["issues"], prog_name="gitp")
    mock_pm_portfoliomanager.assert_called_once()
    mock_pm_portfoliomanager.return_value.create_issues.assert_called_once()


@patch("git_portfolio.portfolio_manager.PortfolioManager", autospec=True)
def test_create_prs(mock_pm_portfoliomanager: Mock, runner: CliRunner) -> None:
    """It call create_pull_requests from pm.PortfolioManager."""
    runner.invoke(__main__.create, ["prs"], prog_name="gitp")
    mock_pm_portfoliomanager.assert_called_once()
    mock_pm_portfoliomanager.return_value.create_pull_requests.assert_called_once()


@patch("git_portfolio.portfolio_manager.PortfolioManager", autospec=True)
def test_merge_prs(mock_pm_portfoliomanager: Mock, runner: CliRunner) -> None:
    """It call merge_pull_requests from pm.PortfolioManager."""
    runner.invoke(__main__.merge, ["prs"], prog_name="gitp")
    mock_pm_portfoliomanager.assert_called_once()
    mock_pm_portfoliomanager.return_value.merge_pull_requests.assert_called_once()


@patch("git_portfolio.portfolio_manager.PortfolioManager", autospec=True)
def test_delete_branches(mock_pm_portfoliomanager: Mock, runner: CliRunner) -> None:
    """It call delete_branches from pm.PortfolioManager."""
    runner.invoke(__main__.delete, ["branches"], prog_name="gitp")
    mock_pm_portfoliomanager.assert_called_once()
    mock_pm_portfoliomanager.return_value.delete_branches.assert_called_once()
