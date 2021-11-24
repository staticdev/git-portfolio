"""Command-line interface."""
from __future__ import annotations

import functools
import sys
from typing import Any
from typing import Callable
from typing import cast
from typing import TypeVar

import click

import git_portfolio.config_manager as cm
import git_portfolio.domain.config as c
import git_portfolio.domain.gh_connection_settings as cs
import git_portfolio.github_service as ghs
import git_portfolio.prompt as p
import git_portfolio.request_objects.issue_list as il
import git_portfolio.responses as res
import git_portfolio.use_cases.config_init as ci
import git_portfolio.use_cases.config_repos as cr
import git_portfolio.use_cases.gh_close_issue as ghcli
import git_portfolio.use_cases.gh_create_issue as ghci
import git_portfolio.use_cases.gh_create_pr as ghcp
import git_portfolio.use_cases.gh_delete_branch as ghdb
import git_portfolio.use_cases.gh_merge_pr as ghmp
import git_portfolio.use_cases.gh_reopen_issue as ghri
import git_portfolio.use_cases.git as git
import git_portfolio.use_cases.git_clone as gcuc
import git_portfolio.use_cases.poetry as poetry


F = TypeVar("F", bound=Callable[..., Any])
CONFIG_MANAGER = cm.ConfigManager()


def gitp_config_check(func: F) -> F:
    """Validate if there are selected repos and outputs success."""

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        if CONFIG_MANAGER.config_is_empty():
            click.secho(
                "Error: no config found, please run `gitp config init`.",
                fg="red",
            )
            sys.exit(3)
        else:
            value = func(*args, **kwargs)
            _echo_outputs(value)
            if not bool(value):
                sys.exit(4)
            return value

    return cast(F, wrapper)


@click.group("cli")
@click.version_option()
def main() -> None:
    """Git Portfolio."""
    pass


def _echo_outputs(response: res.ResponseFailure | res.ResponseSuccess) -> None:
    if bool(response):
        success = cast(res.ResponseSuccess, response)
        click.secho(success.value)
    else:
        click.secho(
            f"Error(s) found during execution:\n{response.value['message']}", fg="red"
        )


def _get_github_service(config: c.Config) -> ghs.GithubService:
    settings = cs.GhConnectionSettings(
        config.github_access_token, config.github_hostname
    )
    try:
        return ghs.GithubService(settings)
    except AttributeError:
        response = res.ResponseFailure(
            res.ResponseTypes.PARAMETERS_ERROR,
            "Wrong GitHub permissions. Please check your token.",
        )
    except ConnectionError:
        response = res.ResponseFailure(
            res.ResponseTypes.SYSTEM_ERROR,
            (
                "Unable to reach server. Please check your network and credentials and "
                "try again."
            ),
        )
    _echo_outputs(response)
    raise click.ClickException("")


@main.command("add")
@click.argument("args", nargs=-1)
@gitp_config_check
def add(args: tuple[str]) -> res.ResponseFailure | res.ResponseSuccess:
    """Batch `git add` command."""
    return git.GitUseCase().execute(
        CONFIG_MANAGER.config.github_selected_repos, "add", args
    )


@main.command("checkout", context_settings={"ignore_unknown_options": True})
@click.argument("args", nargs=-1)
@gitp_config_check
def checkout(args: tuple[str]) -> res.ResponseFailure | res.ResponseSuccess:
    """Batch `git checkout` command."""
    return git.GitUseCase().execute(
        CONFIG_MANAGER.config.github_selected_repos, "checkout", args
    )


@main.command("commit", context_settings={"ignore_unknown_options": True})
@click.argument("args", nargs=-1)
@gitp_config_check
def commit(args: tuple[str]) -> res.ResponseFailure | res.ResponseSuccess:
    """Batch `git commit` command."""
    return git.GitUseCase().execute(
        CONFIG_MANAGER.config.github_selected_repos, "commit", args
    )


@main.command("diff", context_settings={"ignore_unknown_options": True})
@click.argument("args", nargs=-1)
@gitp_config_check
def diff(args: tuple[str]) -> res.ResponseFailure | res.ResponseSuccess:
    """Batch `git diff` command."""
    return git.GitUseCase().execute(
        CONFIG_MANAGER.config.github_selected_repos, "diff", args
    )


@main.command("pull", context_settings={"ignore_unknown_options": True})
@click.argument("args", nargs=-1)
@gitp_config_check
def pull(args: tuple[str]) -> res.ResponseFailure | res.ResponseSuccess:
    """Batch `git pull` command."""
    return git.GitUseCase().execute(
        CONFIG_MANAGER.config.github_selected_repos, "pull", args
    )


@main.command("push", context_settings={"ignore_unknown_options": True})
@click.argument("args", nargs=-1)
@gitp_config_check
def push(args: tuple[str]) -> res.ResponseFailure | res.ResponseSuccess:
    """Batch `git push` command."""
    return git.GitUseCase().execute(
        CONFIG_MANAGER.config.github_selected_repos, "push", args
    )


@main.command("reset", context_settings={"ignore_unknown_options": True})
@click.argument("args", nargs=-1)
@gitp_config_check
def reset(args: tuple[str]) -> res.ResponseFailure | res.ResponseSuccess:
    """Batch `git reset` command."""
    return git.GitUseCase().execute(
        CONFIG_MANAGER.config.github_selected_repos, "reset", args
    )


@main.command("status")
@click.argument("args", nargs=-1)
@gitp_config_check
def status(args: tuple[str]) -> res.ResponseFailure | res.ResponseSuccess:
    """Batch `git status` command."""
    return git.GitUseCase().execute(
        CONFIG_MANAGER.config.github_selected_repos, "status", args
    )


@click.group("config")
def configure() -> None:
    """Config command group."""
    pass


@click.group("create")
def create() -> None:
    """Create command group."""
    pass


@click.group("merge")
def merge() -> None:
    """Merge command group."""
    pass


@click.group("close")
def close() -> None:
    """Close command group."""
    pass


@click.group("delete")
def delete() -> None:
    """Delete command group."""
    pass


@click.group("reopen")
def reopen() -> None:
    """Reopen command group."""
    pass


@configure.command("init")
def config_init() -> None:
    """Initialize `gitp` config."""
    while True:
        settings = p.InquirerPrompter.connect_github(
            CONFIG_MANAGER.config.github_access_token
        )
        response = ci.ConfigInitUseCase(CONFIG_MANAGER).execute(settings)
        if bool(response):
            success = cast(res.ResponseSuccess, response)
            click.secho(success.value)
            break
        else:
            click.secho(f"Error: {response.value['message']}", fg="red")
            if response.type == res.ResponseTypes.SYSTEM_ERROR:
                click.ClickException("")


@configure.command("repos")
@gitp_config_check
def config_repos() -> res.ResponseFailure | res.ResponseSuccess:
    """Configure current working `gitp` repositories."""
    new_repos = p.InquirerPrompter.new_repos(
        CONFIG_MANAGER.config.github_selected_repos
    )
    if not new_repos:
        return res.ResponseSuccess()
    github_service = _get_github_service(CONFIG_MANAGER.config)
    repo_names = github_service.get_repo_names()
    selected_repos = p.InquirerPrompter.select_repos(repo_names)
    return cr.ConfigReposUseCase(CONFIG_MANAGER).execute(
        github_service.get_config(), selected_repos
    )


@main.command("clone")
@gitp_config_check
def clone() -> res.ResponseFailure | res.ResponseSuccess:
    """Batch `git clone` command on current folder. Does not accept aditional args."""
    github_service = _get_github_service(CONFIG_MANAGER.config)
    return gcuc.GitCloneUseCase(github_service).execute(
        CONFIG_MANAGER.config.github_selected_repos
    )


@create.command("issues")
@gitp_config_check
def create_issues() -> res.ResponseFailure | res.ResponseSuccess:
    """Batch creation of issues on GitHub."""
    github_service = _get_github_service(CONFIG_MANAGER.config)
    issue = p.InquirerPrompter.create_issues(
        CONFIG_MANAGER.config.github_selected_repos
    )
    return ghci.GhCreateIssueUseCase(CONFIG_MANAGER, github_service).execute(issue)


@close.command("issues")
@gitp_config_check
def close_issues() -> res.ResponseFailure | res.ResponseSuccess:
    """Batch close issues on GitHub."""
    github_service = _get_github_service(CONFIG_MANAGER.config)
    list_object = "issue"
    title_query = p.InquirerPrompter.query_by_title(
        CONFIG_MANAGER.config.github_selected_repos, list_object
    )
    list_request = il.build_list_request(
        filters={
            "obj__eq": list_object,
            "state__eq": "open",
            "title__contains": title_query,
        }
    )
    return ghcli.GhCloseIssueUseCase(CONFIG_MANAGER, github_service).execute(
        list_request
    )


@reopen.command("issues")
@gitp_config_check
def reopen_issues() -> res.ResponseFailure | res.ResponseSuccess:
    """Batch reopen issues on GitHub."""
    github_service = _get_github_service(CONFIG_MANAGER.config)
    list_object = "issue"
    title_query = p.InquirerPrompter.query_by_title(
        CONFIG_MANAGER.config.github_selected_repos, list_object
    )
    list_request = il.build_list_request(
        filters={
            "obj__eq": list_object,
            "state__eq": "closed",
            "title__contains": title_query,
        }
    )
    return ghri.GhReopenIssueUseCase(CONFIG_MANAGER, github_service).execute(
        list_request
    )


@main.command("poetry", context_settings={"ignore_unknown_options": True})
@click.argument("args", nargs=-1)
@gitp_config_check
def poetry_cmd(args: tuple[str]) -> res.ResponseFailure | res.ResponseSuccess:
    """Batch `poetry` command."""
    return poetry.PoetryUseCase().execute(
        CONFIG_MANAGER.config.github_selected_repos, "poetry", args
    )


@create.command("prs")
@gitp_config_check
def create_prs() -> res.ResponseFailure | res.ResponseSuccess:
    """Batch creation of pull requests on GitHub."""
    github_service = _get_github_service(CONFIG_MANAGER.config)
    pr = p.InquirerPrompter.create_pull_requests(
        CONFIG_MANAGER.config.github_selected_repos
    )
    # list for linked issues
    list_request = il.build_list_request(
        filters={
            "obj__eq": "issue",
            "state__eq": "open",
            "title__contains": pr.issues_title_query,
        }
    )
    return ghcp.GhCreatePrUseCase(CONFIG_MANAGER, github_service).execute(
        pr, list_request
    )


@close.command("prs")
@gitp_config_check
def close_prs() -> res.ResponseFailure | res.ResponseSuccess:
    """Batch close pull requests on GitHub."""
    github_service = _get_github_service(CONFIG_MANAGER.config)
    list_object = "pull request"
    title_query = p.InquirerPrompter.query_by_title(
        CONFIG_MANAGER.config.github_selected_repos, list_object
    )
    list_request = il.build_list_request(
        filters={
            "obj__eq": list_object,
            "state__eq": "open",
            "title__contains": title_query,
        }
    )
    return ghcli.GhCloseIssueUseCase(CONFIG_MANAGER, github_service).execute(
        list_request
    )


@merge.command("prs")
@gitp_config_check
def merge_prs() -> res.ResponseFailure | res.ResponseSuccess:
    """Batch merge of pull requests on GitHub."""
    github_service = _get_github_service(CONFIG_MANAGER.config)
    pr_merge = p.InquirerPrompter.merge_pull_requests(
        github_service.get_username(),
        CONFIG_MANAGER.config.github_selected_repos,
    )
    return ghmp.GhMergePrUseCase(CONFIG_MANAGER, github_service).execute(pr_merge)


@delete.command("branches")
@gitp_config_check
def delete_branches() -> res.ResponseFailure | res.ResponseSuccess:
    """Batch deletion of branches on GitHub."""
    github_service = _get_github_service(CONFIG_MANAGER.config)
    branch = p.InquirerPrompter.delete_branches(
        CONFIG_MANAGER.config.github_selected_repos
    )
    return ghdb.GhDeleteBranchUseCase(CONFIG_MANAGER, github_service).execute(branch)


main.add_command(configure)
main.add_command(create)
main.add_command(close)
main.add_command(merge)
main.add_command(delete)
main.add_command(reopen)


if __name__ == "__main__":
    main(prog_name="gitp")  # pragma: no cover
