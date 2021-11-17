"""Test cases for the __main__ module."""
import pytest
from click.testing import CliRunner
from pytest_mock import MockerFixture

import git_portfolio.__main__
import git_portfolio.domain.config as c
import git_portfolio.responses as res


REPO = "org/repo-name"
REPO2 = "org/repo-name2"


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
def mock_git_status_use_case(mocker: MockerFixture) -> MockerFixture:
    """Fixture for mocking GitStatusUseCase."""
    return mocker.patch(
        "git_portfolio.use_cases.git_status_use_case.GitStatusUseCase", autospec=True
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
    def _() -> res.ResponseSuccess:
        return res.ResponseSuccess("success message")

    result = runner.invoke(git_portfolio.__main__.main, ["test"], prog_name="gitp")

    assert "success message" in result.output


def test_gitp_config_check_execute_error(
    mock_config_manager: MockerFixture, runner: CliRunner
) -> None:
    """It calls a command an error response."""

    @git_portfolio.__main__.main.command("test")
    @git_portfolio.__main__.gitp_config_check
    def _() -> res.ResponseFailure:
        return res.ResponseFailure(res.ResponseTypes.SYSTEM_ERROR, "some error msg")

    result = runner.invoke(git_portfolio.__main__.main, ["test"], prog_name="gitp")

    assert "Error(s) found during execution:\nsome error msg" in result.output
    assert result.exit_code == 4


def test_gitp_config_check_no_repos(
    mock_config_manager: MockerFixture, runner: CliRunner
) -> None:
    """It outputs no repos selected error message."""

    @git_portfolio.__main__.main.command("test")
    @git_portfolio.__main__.gitp_config_check
    def _() -> res.ResponseFailure:
        return res.ResponseFailure(res.ResponseTypes.SYSTEM_ERROR, "some error msg")

    mock_config_manager.config_is_empty.return_value = True
    result = runner.invoke(git_portfolio.__main__.main, ["test"], prog_name="gitp")

    assert result.output.startswith("Error: no config found")
    assert result.exit_code == 3


def test_add_success(
    mock_git_use_case: MockerFixture,
    mock_config_manager: MockerFixture,
    runner: CliRunner,
) -> None:
    """It calls add with '.'."""
    runner.invoke(git_portfolio.__main__.main, ["add", "."], prog_name="gitp")

    mock_git_use_case.return_value.execute.assert_called_once_with(
        [REPO], "add", (".",)
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


def test_checkout_success(
    mock_git_use_case: MockerFixture,
    mock_config_manager: MockerFixture,
    runner: CliRunner,
) -> None:
    """It calls checkout with main."""
    runner.invoke(git_portfolio.__main__.main, ["checkout", "main"], prog_name="gitp")

    mock_git_use_case.return_value.execute.assert_called_once_with(
        [REPO], "checkout", ("main",)
    )


def test_checkout_new_branch(
    mock_git_use_case: MockerFixture,
    mock_config_manager: MockerFixture,
    runner: CliRunner,
) -> None:
    """It calls checkout with main."""
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


def test_reset_success(
    mock_git_use_case: MockerFixture,
    mock_config_manager: MockerFixture,
    runner: CliRunner,
) -> None:
    """It calls reset with HEAD^."""
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


def test_status_success(
    mock_git_use_case: MockerFixture,
    mock_config_manager: MockerFixture,
    runner: CliRunner,
) -> None:
    """It calls status."""
    runner.invoke(git_portfolio.__main__.main, ["status"], prog_name="gitp")

    mock_git_use_case.return_value.execute.assert_called_once_with([REPO], "status", ())


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
    result = runner.invoke(git_portfolio.__main__.configure, ["init"], prog_name="gitp")

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
    result = runner.invoke(git_portfolio.__main__.configure, ["init"], prog_name="gitp")

    assert mock_config_init_use_case(config_manager).execute.call_count == 2
    assert result.output == "Error: message\nsuccess message\n"


def test_config_init_connection_error(
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
    result = runner.invoke(git_portfolio.__main__.configure, ["init"], prog_name="gitp")

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
        git_portfolio.__main__.configure, ["repos"], prog_name="gitp"
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
        git_portfolio.__main__.configure, ["repos"], prog_name="gitp"
    )

    assert result.exit_code == 0


def test_config_repos_wrong_token(
    mock_prompt_inquirer_prompter: MockerFixture,
    mock_github_service: MockerFixture,
    mock_config_manager: MockerFixture,
    runner: CliRunner,
) -> None:
    """It executes _get_github_service with token error."""
    mock_config_manager.config_is_empty.return_value = False
    mock_prompt_inquirer_prompter.new_repos.return_value = True
    mock_github_service.side_effect = AttributeError
    result = runner.invoke(
        git_portfolio.__main__.configure, ["repos"], prog_name="gitp"
    )

    assert result.output.startswith(
        "Error(s) found during execution:\nWrong GitHub permissions. Please check your"
        " token.\n"
    )
    assert type(result.exception) == SystemExit


def test_config_repos_connection_error(
    mock_prompt_inquirer_prompter: MockerFixture,
    mock_github_service: MockerFixture,
    mock_config_manager: MockerFixture,
    runner: CliRunner,
) -> None:
    """It executes _get_github_service with token error."""
    mock_config_manager.config_is_empty.return_value = False
    mock_prompt_inquirer_prompter.new_repos.return_value = True
    mock_github_service.side_effect = ConnectionError
    result = runner.invoke(
        git_portfolio.__main__.configure, ["repos"], prog_name="gitp"
    )

    assert result.output.startswith(
        "Error(s) found during execution:\nUnable to reach server. Please check "
        "your network and credentials and try again.\n"
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
    runner.invoke(git_portfolio.__main__.create, ["issues"], prog_name="gitp")

    mock_gh_create_issue_use_case(
        config_manager, github_service
    ).execute.assert_called_once()


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
    runner.invoke(git_portfolio.__main__.close, ["issues"], prog_name="gitp")

    mock_gh_close_issue_use_case(
        config_manager, github_service
    ).execute.assert_called_once()


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
    runner.invoke(git_portfolio.__main__.reopen, ["issues"], prog_name="gitp")

    mock_gh_reopen_issue_use_case(
        config_manager, github_service
    ).execute.assert_called_once()


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
    runner.invoke(git_portfolio.__main__.create, ["prs"], prog_name="gitp")

    mock_gh_create_pr_use_case(
        config_manager, github_service
    ).execute.assert_called_once()


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
    runner.invoke(git_portfolio.__main__.close, ["prs"], prog_name="gitp")

    mock_gh_close_issue_use_case(
        config_manager, github_service
    ).execute.assert_called_once()


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
    runner.invoke(git_portfolio.__main__.merge, ["prs"], prog_name="gitp")

    mock_gh_merge_pr_use_case(
        config_manager, github_service
    ).execute.assert_called_once()


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
    runner.invoke(git_portfolio.__main__.delete, ["branches"], prog_name="gitp")

    mock_gh_delete_branch_use_case(
        config_manager, github_service
    ).execute.assert_called_once()
