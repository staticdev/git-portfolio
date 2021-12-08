"""Test cases for the __main__ module."""
from __future__ import annotations

import pytest
from click.testing import CliRunner
from pytest_mock import MockerFixture
from tests.conftest import REPO

import git_portfolio.__main__
import git_portfolio.domain.config as c
import git_portfolio.github_service as gs
import git_portfolio.responses as res


@pytest.fixture
def runner() -> CliRunner:
    """Fixture for invoking command-line interfaces."""
    return CliRunner()


@pytest.fixture
def mock_config_manager(mocker: MockerFixture) -> MockerFixture:
    """Fixture for mocking CONFIG_MANAGER."""
    mock = mocker.patch("git_portfolio.__main__.CONFIG_MANAGER")
    mock.config_is_empty.return_value = False
    mock.config.github_selected_repos = [REPO]
    return mock


@pytest.fixture
def mock_github_service(mocker: MockerFixture) -> MockerFixture:
    """Fixture for mocking GithubService."""
    return mocker.patch("git_portfolio.github_service.GithubService", autospec=True)


@pytest.fixture
def mock_github_service_error(mocker: MockerFixture) -> MockerFixture:
    """Fixture for mocking GithubService with error."""
    return mocker.patch(
        "git_portfolio.github_service.GithubService",
        autospec=True,
        side_effect=gs.GithubServiceError,
    )


@pytest.fixture
def mock_config_init_use_case(mocker: MockerFixture) -> MockerFixture:
    """Fixture for mocking ConfigInitUseCase."""
    return mocker.patch(
        "git_portfolio.use_cases.config_init.ConfigInitUseCase", autospec=True
    )


@pytest.fixture
def mock_config_repos_use_case(mocker: MockerFixture) -> MockerFixture:
    """Fixture for mocking ConfigReposUseCase."""
    return mocker.patch(
        "git_portfolio.use_cases.config_repos.ConfigReposUseCase",
        autospec=True,
    )


@pytest.fixture
def mock_git_clone_use_case(mocker: MockerFixture) -> MockerFixture:
    """Fixture for mocking GitCloneUseCase."""
    return mocker.patch(
        "git_portfolio.use_cases.git_clone.GitCloneUseCase", autospec=True
    )


@pytest.fixture
def mock_git_use_case(mocker: MockerFixture) -> MockerFixture:
    """Fixture for mocking GitUseCase."""
    return mocker.patch("git_portfolio.use_cases.git.GitUseCase", autospec=True)


@pytest.fixture
def mock_gh_create_issue_use_case(mocker: MockerFixture) -> MockerFixture:
    """Fixture for mocking GhCreateIssueUseCase."""
    return mocker.patch(
        "git_portfolio.use_cases.gh_create_issue.GhCreateIssueUseCase",
        autospec=True,
    )


@pytest.fixture
def mock_gh_close_issue_use_case(mocker: MockerFixture) -> MockerFixture:
    """Fixture for mocking GhCloseIssueUseCase."""
    return mocker.patch(
        "git_portfolio.use_cases.gh_close_issue.GhCloseIssueUseCase",
        autospec=True,
    )


@pytest.fixture
def mock_gh_reopen_issue_use_case(mocker: MockerFixture) -> MockerFixture:
    """Fixture for mocking GhReopenIssueUseCase."""
    return mocker.patch(
        "git_portfolio.use_cases.gh_reopen_issue.GhReopenIssueUseCase",
        autospec=True,
    )


@pytest.fixture
def mock_gh_create_pr_use_case(mocker: MockerFixture) -> MockerFixture:
    """Fixture for mocking GhCreatePrUseCase."""
    return mocker.patch(
        "git_portfolio.use_cases.gh_create_pr.GhCreatePrUseCase",
        autospec=True,
    )


@pytest.fixture
def mock_gh_merge_pr_use_case(mocker: MockerFixture) -> MockerFixture:
    """Fixture for mocking GhMergePrUseCase."""
    return mocker.patch(
        "git_portfolio.use_cases.gh_merge_pr.GhMergePrUseCase",
        autospec=True,
    )


@pytest.fixture
def mock_gh_delete_branch_use_case(mocker: MockerFixture) -> MockerFixture:
    """Fixture for mocking GhDeleteBranchUseCase."""
    return mocker.patch(
        "git_portfolio.use_cases.gh_delete_branch.GhDeleteBranchUseCase",
        autospec=True,
    )


@pytest.fixture
def mock_poetry_use_case(mocker: MockerFixture) -> MockerFixture:
    """Fixture for mocking PoetryUseCase."""
    return mocker.patch(
        "git_portfolio.use_cases.poetry.PoetryUseCase",
        autospec=True,
    )


@pytest.fixture
def mock_prompt_inquirer_prompter(mocker: MockerFixture) -> MockerFixture:
    """Fixture for mocking prompt.InquirerPrompter."""
    return mocker.patch("git_portfolio.prompt.InquirerPrompter", autospec=True)


def test_gitp_config_check_success(
    mock_config_manager: MockerFixture, runner: CliRunner
) -> None:
    """It outputs success message."""

    @git_portfolio.__main__.main.command("test")
    @git_portfolio.__main__.gitp_config_check
    def _() -> list[res.ResponseSuccess]:
        return [res.ResponseSuccess("success message")]

    result = runner.invoke(git_portfolio.__main__.main, ["test"], prog_name="gitp")

    assert "success message" in result.output


def test_gitp_config_check_execute_error(
    mock_config_manager: MockerFixture, runner: CliRunner
) -> None:
    """It calls a command an error response."""

    @git_portfolio.__main__.main.command("test")
    @git_portfolio.__main__.gitp_config_check
    def _() -> list[res.ResponseFailure]:
        return [res.ResponseFailure(res.ResponseTypes.SYSTEM_ERROR, "some error msg")]

    result = runner.invoke(git_portfolio.__main__.main, ["test"], prog_name="gitp")

    assert "some error msg" in result.output
    assert result.exit_code == 4


def test_gitp_config_check_no_repos(
    mock_config_manager: MockerFixture, runner: CliRunner
) -> None:
    """It outputs no repos selected error message."""
    mock_config_manager.config_is_empty.return_value = True
    result = runner.invoke(git_portfolio.__main__.main, ["test"], prog_name="gitp")

    assert result.output.startswith("Error: no config found")
    assert result.exit_code == 3


def test_add_success(
    mock_git_use_case: MockerFixture,
    mock_config_manager: MockerFixture,
    runner: CliRunner,
) -> None:
    """It calls add."""
    runner.invoke(git_portfolio.__main__.main, ["add", "."], prog_name="gitp")

    mock_git_use_case.return_value.execute.assert_called_once_with(
        [REPO], "add", (".",)
    )


def test_branch_success(
    mock_git_use_case: MockerFixture,
    mock_config_manager: MockerFixture,
    runner: CliRunner,
) -> None:
    """It calls branch."""
    runner.invoke(git_portfolio.__main__.main, ["branch", "-a"], prog_name="gitp")

    mock_git_use_case.return_value.execute.assert_called_once_with(
        [REPO], "branch", ("-a",)
    )


def test_poetry_success(
    mock_poetry_use_case: MockerFixture,
    mock_config_manager: MockerFixture,
    runner: CliRunner,
) -> None:
    """It calls poetry with 'version'."""
    runner.invoke(git_portfolio.__main__.main, ["poetry", "version"], prog_name="gitp")

    mock_poetry_use_case.return_value.execute.assert_called_once_with(
        [REPO], "poetry", ("version",)
    )


def test_poetry_with_options_success(
    mock_poetry_use_case: MockerFixture,
    mock_config_manager: MockerFixture,
    runner: CliRunner,
) -> None:
    """It calls poetry with 'add pytest --group test'."""
    runner.invoke(
        git_portfolio.__main__.main,
        ["poetry", "add", "pytest", "--group", "test"],
        prog_name="gitp",
    )

    mock_poetry_use_case.return_value.execute.assert_called_once_with(
        [REPO], "poetry", ("add", "pytest", "--group", "test")
    )


def test_checkout_success(
    mock_git_use_case: MockerFixture,
    mock_config_manager: MockerFixture,
    runner: CliRunner,
) -> None:
    """It calls checkout."""
    runner.invoke(git_portfolio.__main__.main, ["checkout", "main"], prog_name="gitp")

    mock_git_use_case.return_value.execute.assert_called_once_with(
        [REPO], "checkout", ("main",)
    )


def test_checkout_new_branch(
    mock_git_use_case: MockerFixture,
    mock_config_manager: MockerFixture,
    runner: CliRunner,
) -> None:
    """It calls checkout to create new branch."""
    runner.invoke(
        git_portfolio.__main__.main, ["checkout", "-b", "new-branch"], prog_name="gitp"
    )

    mock_git_use_case.return_value.execute.assert_called_once_with(
        [REPO],
        "checkout",
        (
            "-b",
            "new-branch",
        ),
    )


def test_commit_success(
    mock_git_use_case: MockerFixture,
    mock_config_manager: MockerFixture,
    runner: CliRunner,
) -> None:
    """It calls commit with message."""
    runner.invoke(
        git_portfolio.__main__.main, ["commit", "-m", "message"], prog_name="gitp"
    )

    mock_git_use_case.return_value.execute.assert_called_once_with(
        [REPO], "commit", ("-m", "message")
    )


def test_diff_success(
    mock_git_use_case: MockerFixture,
    mock_config_manager: MockerFixture,
    runner: CliRunner,
) -> None:
    """It calls diff."""
    runner.invoke(git_portfolio.__main__.main, ["diff"], prog_name="gitp")

    mock_git_use_case.return_value.execute.assert_called_once_with([REPO], "diff", ())


def test_fetch_success(
    mock_git_use_case: MockerFixture,
    mock_config_manager: MockerFixture,
    runner: CliRunner,
) -> None:
    """It calls fetch."""
    runner.invoke(git_portfolio.__main__.main, ["fetch"], prog_name="gitp")

    mock_git_use_case.return_value.execute.assert_called_once_with([REPO], "fetch", ())


def test_init_success(
    mock_git_use_case: MockerFixture,
    mock_config_manager: MockerFixture,
    runner: CliRunner,
) -> None:
    """It calls init."""
    runner.invoke(git_portfolio.__main__.main, ["init"], prog_name="gitp")

    mock_git_use_case.return_value.execute.assert_called_once_with([REPO], "init", ())


def test_merge_success(
    mock_git_use_case: MockerFixture,
    mock_config_manager: MockerFixture,
    runner: CliRunner,
) -> None:
    """It calls merge."""
    runner.invoke(git_portfolio.__main__.main, ["merge"], prog_name="gitp")

    mock_git_use_case.return_value.execute.assert_called_once_with([REPO], "merge", ())


def test_mv_success(
    mock_git_use_case: MockerFixture,
    mock_config_manager: MockerFixture,
    runner: CliRunner,
) -> None:
    """It calls mv."""
    runner.invoke(git_portfolio.__main__.main, ["mv"], prog_name="gitp")

    mock_git_use_case.return_value.execute.assert_called_once_with([REPO], "mv", ())


def test_pull_success(
    mock_git_use_case: MockerFixture,
    mock_config_manager: MockerFixture,
    runner: CliRunner,
) -> None:
    """It calls pull."""
    runner.invoke(git_portfolio.__main__.main, ["pull"], prog_name="gitp")

    mock_git_use_case.return_value.execute.assert_called_once_with([REPO], "pull", ())


def test_pull_rebase_success(
    mock_git_use_case: MockerFixture,
    mock_config_manager: MockerFixture,
    runner: CliRunner,
) -> None:
    """It calls pull."""
    runner.invoke(git_portfolio.__main__.main, ["pull", "--rebase"], prog_name="gitp")

    mock_git_use_case.return_value.execute.assert_called_once_with(
        [REPO], "pull", ("--rebase",)
    )


def test_push_success(
    mock_git_use_case: MockerFixture,
    mock_config_manager: MockerFixture,
    runner: CliRunner,
) -> None:
    """It calls push with origin main."""
    runner.invoke(
        git_portfolio.__main__.main, ["push", "origin", "main"], prog_name="gitp"
    )

    mock_git_use_case.return_value.execute.assert_called_once_with(
        [REPO], "push", ("origin", "main")
    )


def test_push_with_extra_arguments(
    mock_git_use_case: MockerFixture,
    mock_config_manager: MockerFixture,
    runner: CliRunner,
) -> None:
    """It calls push with --set-upstream origin new-branch."""
    runner.invoke(
        git_portfolio.__main__.main,
        ["push", "--set-upstream", "origin", "new-branch"],
        prog_name="gitp",
    )

    mock_git_use_case.return_value.execute.assert_called_once_with(
        [REPO], "push", ("--set-upstream", "origin", "new-branch")
    )


def test_rebase_success(
    mock_git_use_case: MockerFixture,
    mock_config_manager: MockerFixture,
    runner: CliRunner,
) -> None:
    """It calls rebase."""
    runner.invoke(git_portfolio.__main__.main, ["rebase"], prog_name="gitp")

    mock_git_use_case.return_value.execute.assert_called_once_with([REPO], "rebase", ())


def test_reset_success(
    mock_git_use_case: MockerFixture,
    mock_config_manager: MockerFixture,
    runner: CliRunner,
) -> None:
    """It calls reset."""
    runner.invoke(git_portfolio.__main__.main, ["reset", "HEAD^"], prog_name="gitp")

    mock_git_use_case.return_value.execute.assert_called_once_with(
        [REPO], "reset", ("HEAD^",)
    )


def test_reset_success_with_hard(
    mock_git_use_case: MockerFixture,
    mock_config_manager: MockerFixture,
    runner: CliRunner,
) -> None:
    """It calls reset with --hard HEAD^."""
    runner.invoke(
        git_portfolio.__main__.main, ["reset", "--hard", "HEAD^"], prog_name="gitp"
    )

    mock_git_use_case.return_value.execute.assert_called_once_with(
        [REPO], "reset", ("--hard", "HEAD^")
    )


def test_rm_success(
    mock_git_use_case: MockerFixture,
    mock_config_manager: MockerFixture,
    runner: CliRunner,
) -> None:
    """It calls rm."""
    runner.invoke(git_portfolio.__main__.main, ["rm"], prog_name="gitp")

    mock_git_use_case.return_value.execute.assert_called_once_with([REPO], "rm", ())


def test_show_success(
    mock_git_use_case: MockerFixture,
    mock_config_manager: MockerFixture,
    runner: CliRunner,
) -> None:
    """It calls show."""
    runner.invoke(git_portfolio.__main__.main, ["show"], prog_name="gitp")

    mock_git_use_case.return_value.execute.assert_called_once_with([REPO], "show", ())


def test_status_success(
    mock_git_use_case: MockerFixture,
    mock_config_manager: MockerFixture,
    runner: CliRunner,
) -> None:
    """It calls status."""
    runner.invoke(git_portfolio.__main__.main, ["status"], prog_name="gitp")

    mock_git_use_case.return_value.execute.assert_called_once_with([REPO], "status", ())


def test_switch_success(
    mock_git_use_case: MockerFixture,
    mock_config_manager: MockerFixture,
    runner: CliRunner,
) -> None:
    """It calls switch."""
    runner.invoke(git_portfolio.__main__.main, ["switch"], prog_name="gitp")

    mock_git_use_case.return_value.execute.assert_called_once_with([REPO], "switch", ())


def test_tag_success(
    mock_git_use_case: MockerFixture,
    mock_config_manager: MockerFixture,
    runner: CliRunner,
) -> None:
    """It calls tag."""
    runner.invoke(git_portfolio.__main__.main, ["tag"], prog_name="gitp")

    mock_git_use_case.return_value.execute.assert_called_once_with([REPO], "tag", ())


def test_config_init_success(
    mock_prompt_inquirer_prompter: MockerFixture,
    mock_config_manager: MockerFixture,
    mock_config_init_use_case: MockerFixture,
    runner: CliRunner,
) -> None:
    """It executes config init use case."""
    config_manager = mock_config_manager.return_value
    mock_config_init_use_case(
        config_manager
    ).execute.return_value = res.ResponseSuccess("success message")
    result = runner.invoke(
        git_portfolio.__main__.group_config, ["init"], prog_name="gitp"
    )

    mock_config_init_use_case(config_manager).execute.assert_called_once()
    assert result.output == "success message\n"


def test_config_init_wrong_token(
    mock_prompt_inquirer_prompter: MockerFixture,
    mock_config_manager: MockerFixture,
    mock_config_init_use_case: MockerFixture,
    runner: CliRunner,
) -> None:
    """It executes with token error first then succeeds."""
    config_manager = mock_config_manager.return_value
    mock_config_init_use_case(config_manager).execute.side_effect = [
        res.ResponseFailure(res.ResponseTypes.PARAMETERS_ERROR, "message"),
        res.ResponseSuccess("success message"),
    ]
    result = runner.invoke(
        git_portfolio.__main__.group_config, ["init"], prog_name="gitp"
    )

    assert mock_config_init_use_case(config_manager).execute.call_count == 2
    assert result.output == "Error: message\nsuccess message\n"


def test_config_init_service_error(
    mock_prompt_inquirer_prompter: MockerFixture,
    mock_config_manager: MockerFixture,
    mock_config_init_use_case: MockerFixture,
    runner: CliRunner,
) -> None:
    """It executes with connection error first then succeeds."""
    config_manager = mock_config_manager.return_value
    mock_config_init_use_case(config_manager).execute.side_effect = [
        res.ResponseFailure(res.ResponseTypes.SYSTEM_ERROR, "message"),
        res.ResponseSuccess("success message"),
    ]
    result = runner.invoke(
        git_portfolio.__main__.group_config, ["init"], prog_name="gitp"
    )

    assert mock_config_init_use_case(config_manager).execute.call_count == 2
    assert result.output == "Error: message\nsuccess message\n"


def test_config_repos_success(
    mock_prompt_inquirer_prompter: MockerFixture,
    mock_github_service: MockerFixture,
    mock_config_manager: MockerFixture,
    mock_config_repos_use_case: MockerFixture,
    runner: CliRunner,
) -> None:
    """It executes config repos use case."""
    config_manager = mock_config_manager.return_value
    mock_config_manager.config_is_empty.return_value = False
    mock_prompt_inquirer_prompter.new_repos.return_value = True
    mock_config_repos_use_case(
        config_manager
    ).execute.return_value = res.ResponseSuccess("success message")
    result = runner.invoke(
        git_portfolio.__main__.group_config, ["repos"], prog_name="gitp"
    )

    mock_config_repos_use_case(config_manager).execute.assert_called_once()
    assert result.output == "success message\n"


def test_config_repos_do_not_change(
    mock_prompt_inquirer_prompter: MockerFixture,
    mock_config_manager: MockerFixture,
    runner: CliRunner,
) -> None:
    """It does not change config file."""
    mock_config_manager.config_is_empty.return_value = False
    mock_prompt_inquirer_prompter.new_repos.return_value = False
    result = runner.invoke(
        git_portfolio.__main__.group_config, ["repos"], prog_name="gitp"
    )

    assert result.exit_code == 0


def test_config_repos_service_error(
    mock_prompt_inquirer_prompter: MockerFixture,
    mock_github_service_error: MockerFixture,
    mock_config_manager: MockerFixture,
    runner: CliRunner,
) -> None:
    """It raises system exit."""
    mock_config_manager.config_is_empty.return_value = False
    mock_prompt_inquirer_prompter.new_repos.return_value = True
    result = runner.invoke(
        git_portfolio.__main__.group_config, ["repos"], prog_name="gitp"
    )

    assert type(result.exception) == SystemExit


def test_clone_success(
    mock_git_clone_use_case: MockerFixture,
    mock_github_service: MockerFixture,
    mock_config_manager: MockerFixture,
    runner: CliRunner,
) -> None:
    """It calls git clone."""
    github_service = mock_github_service.return_value
    runner.invoke(git_portfolio.__main__.main, ["clone"], prog_name="gitp")

    mock_git_clone_use_case(github_service).execute.assert_called_once_with([REPO])


def test_clone_service_error(
    mock_github_service_error: MockerFixture,
    mock_config_manager: MockerFixture,
    runner: CliRunner,
) -> None:
    """It raises system exit."""
    result = runner.invoke(git_portfolio.__main__.main, ["clone"], prog_name="gitp")

    assert type(result.exception) == SystemExit


def test_create_issues(
    mock_gh_create_issue_use_case: MockerFixture,
    mock_github_service: MockerFixture,
    mock_prompt_inquirer_prompter: MockerFixture,
    mock_config_manager: MockerFixture,
    runner: CliRunner,
) -> None:
    """It executes gh_create_issue."""
    config_manager = mock_config_manager.return_value
    github_service = mock_github_service.return_value
    runner.invoke(git_portfolio.__main__.group_issues, ["create"], prog_name="gitp")

    mock_gh_create_issue_use_case(
        config_manager, github_service
    ).execute.assert_called_once()


def test_create_issues_service_error(
    mock_github_service_error: MockerFixture,
    mock_config_manager: MockerFixture,
    runner: CliRunner,
) -> None:
    """It raises system exit."""
    result = runner.invoke(
        git_portfolio.__main__.group_issues, ["create"], prog_name="gitp"
    )

    assert type(result.exception) == SystemExit


def test_close_issues(
    mock_gh_close_issue_use_case: MockerFixture,
    mock_github_service: MockerFixture,
    mock_prompt_inquirer_prompter: MockerFixture,
    mock_config_manager: MockerFixture,
    runner: CliRunner,
) -> None:
    """It executes gh_close_issue."""
    config_manager = mock_config_manager.return_value
    github_service = mock_github_service.return_value
    runner.invoke(git_portfolio.__main__.group_issues, ["close"], prog_name="gitp")

    mock_gh_close_issue_use_case(
        config_manager, github_service
    ).execute.assert_called_once()


def test_close_issues_service_error(
    mock_github_service_error: MockerFixture,
    mock_config_manager: MockerFixture,
    runner: CliRunner,
) -> None:
    """It raises system exit."""
    result = runner.invoke(
        git_portfolio.__main__.group_issues, ["close"], prog_name="gitp"
    )

    assert type(result.exception) == SystemExit


def test_reopen_issues(
    mock_gh_reopen_issue_use_case: MockerFixture,
    mock_github_service: MockerFixture,
    mock_prompt_inquirer_prompter: MockerFixture,
    mock_config_manager: MockerFixture,
    runner: CliRunner,
) -> None:
    """It executes gh_reopen_issue."""
    config_manager = mock_config_manager.return_value
    github_service = mock_github_service.return_value
    runner.invoke(git_portfolio.__main__.group_issues, ["reopen"], prog_name="gitp")

    mock_gh_reopen_issue_use_case(
        config_manager, github_service
    ).execute.assert_called_once()


def test_reopen_issues_service_error(
    mock_github_service_error: MockerFixture,
    mock_config_manager: MockerFixture,
    runner: CliRunner,
) -> None:
    """It raises system exit."""
    result = runner.invoke(
        git_portfolio.__main__.group_issues, ["reopen"], prog_name="gitp"
    )

    assert type(result.exception) == SystemExit


def test_create_prs(
    mock_gh_create_pr_use_case: MockerFixture,
    mock_github_service: MockerFixture,
    mock_prompt_inquirer_prompter: MockerFixture,
    mock_config_manager: MockerFixture,
    runner: CliRunner,
) -> None:
    """It executes gh_create_pr."""
    config_manager = mock_config_manager.return_value
    github_service = mock_github_service.return_value
    runner.invoke(git_portfolio.__main__.group_prs, ["create"], prog_name="gitp")

    mock_gh_create_pr_use_case(
        config_manager, github_service
    ).execute.assert_called_once()


def test_create_prs_service_error(
    mock_github_service_error: MockerFixture,
    mock_config_manager: MockerFixture,
    runner: CliRunner,
) -> None:
    """It raises system exit."""
    result = runner.invoke(
        git_portfolio.__main__.group_prs, ["create"], prog_name="gitp"
    )

    assert type(result.exception) == SystemExit


def test_close_prs(
    mock_gh_close_issue_use_case: MockerFixture,
    mock_github_service: MockerFixture,
    mock_prompt_inquirer_prompter: MockerFixture,
    mock_config_manager: MockerFixture,
    runner: CliRunner,
) -> None:
    """It executes gh_close_issue."""
    config_manager = mock_config_manager.return_value
    github_service = mock_github_service.return_value
    runner.invoke(git_portfolio.__main__.group_prs, ["close"], prog_name="gitp")

    mock_gh_close_issue_use_case(
        config_manager, github_service
    ).execute.assert_called_once()


def test_close_prs_service_error(
    mock_github_service_error: MockerFixture,
    mock_config_manager: MockerFixture,
    runner: CliRunner,
) -> None:
    """It raises system exit."""
    result = runner.invoke(
        git_portfolio.__main__.group_prs, ["close"], prog_name="gitp"
    )

    assert type(result.exception) == SystemExit


def test_merge_prs(
    mock_gh_merge_pr_use_case: MockerFixture,
    mock_github_service: MockerFixture,
    mock_prompt_inquirer_prompter: MockerFixture,
    mock_config_manager: MockerFixture,
    runner: CliRunner,
) -> None:
    """It executes gh_merge_pr."""
    config_manager = mock_config_manager.return_value
    github_service = mock_github_service.return_value
    github_service.github_username = "user"
    github_service.config = c.Config("", "abc", [REPO])
    runner.invoke(git_portfolio.__main__.group_prs, ["merge"], prog_name="gitp")

    mock_gh_merge_pr_use_case(
        config_manager, github_service
    ).execute.assert_called_once()


def test_merge_prs_service_error(
    mock_github_service_error: MockerFixture,
    mock_config_manager: MockerFixture,
    runner: CliRunner,
) -> None:
    """It raises system exit."""
    result = runner.invoke(
        git_portfolio.__main__.group_prs, ["merge"], prog_name="gitp"
    )

    assert type(result.exception) == SystemExit


def test_delete_branches(
    mock_gh_delete_branch_use_case: MockerFixture,
    mock_github_service: MockerFixture,
    mock_prompt_inquirer_prompter: MockerFixture,
    mock_config_manager: MockerFixture,
    runner: CliRunner,
) -> None:
    """It call delete_branches from pm.GithubService."""
    config_manager = mock_config_manager.return_value
    github_service = mock_github_service.return_value
    runner.invoke(git_portfolio.__main__.group_branches, ["delete"], prog_name="gitp")

    mock_gh_delete_branch_use_case(
        config_manager, github_service
    ).execute.assert_called_once()


def test_delete_branches_service_error(
    mock_github_service_error: MockerFixture,
    mock_config_manager: MockerFixture,
    runner: CliRunner,
) -> None:
    """It raises system exit."""
    result = runner.invoke(
        git_portfolio.__main__.group_branches, ["delete"], prog_name="gitp"
    )

    assert type(result.exception) == SystemExit
