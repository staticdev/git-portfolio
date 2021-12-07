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


def _echo_outputs(responses: list[res.Response]) -> None:
    for response in responses:
        if bool(response):
            success = cast(res.ResponseSuccess, response)
            click.secho(success.value)
        else:
            failure = cast(res.ResponseFailure, response)
            click.secho(f"{failure.value['message']}", fg="red")


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
            responses = func(*args, **kwargs)
            _echo_outputs(responses)
            for response in responses:
                if not bool(response):
                    sys.exit(4)
            return responses

    return cast(F, wrapper)


@click.group("cli")
@click.version_option()
def main() -> None:
    """Git Portfolio."""
    pass


def _get_connection_settings(config: c.Config) -> cs.GhConnectionSettings:
    return cs.GhConnectionSettings(config.github_access_token, config.github_hostname)


@gitp_config_check
def _call_git_use_case(command: str, args: tuple[str]) -> list[res.Response]:
    return git.GitUseCase().execute(
        CONFIG_MANAGER.config.github_selected_repos, command, args
    )


@main.command(context_settings={"ignore_unknown_options": True})
@click.argument("args", nargs=-1)
def add(args: tuple[str]) -> list[res.Response]:
    """Batch `git add` command."""
    return _call_git_use_case("add", args)


@main.command(context_settings={"ignore_unknown_options": True})
@click.argument("args", nargs=-1)
def branch(args: tuple[str]) -> list[res.Response]:
    """Batch `git branch` command."""
    return _call_git_use_case("branch", args)


@main.command(context_settings={"ignore_unknown_options": True})
@click.argument("args", nargs=-1)
def checkout(args: tuple[str]) -> list[res.Response]:
    """Batch `git checkout` command."""
    return _call_git_use_case("checkout", args)


@main.command()
@gitp_config_check
def clone() -> list[res.Response]:
    """Batch `git clone` command on current folder. Does not accept aditional args."""
    settings = _get_connection_settings(CONFIG_MANAGER.config)
    try:
        github_service = ghs.GithubService(settings)
    except ghs.GithubServiceError as gse:
        return [res.ResponseFailure(res.ResponseTypes.RESOURCE_ERROR, gse)]

    return gcuc.GitCloneUseCase(github_service).execute(
        CONFIG_MANAGER.config.github_selected_repos
    )


@main.command(context_settings={"ignore_unknown_options": True})
@click.argument("args", nargs=-1)
def commit(args: tuple[str]) -> list[res.Response]:
    """Batch `git commit` command."""
    return _call_git_use_case("commit", args)


@main.command(context_settings={"ignore_unknown_options": True})
@click.argument("args", nargs=-1)
def diff(args: tuple[str]) -> list[res.Response]:
    """Batch `git diff` command."""
    return _call_git_use_case("diff", args)


@main.command(context_settings={"ignore_unknown_options": True})
@click.argument("args", nargs=-1)
def fetch(args: tuple[str]) -> list[res.Response]:
    """Batch `git fetch` command."""
    return _call_git_use_case("fetch", args)


@main.command(context_settings={"ignore_unknown_options": True})
@click.argument("args", nargs=-1)
def init(args: tuple[str]) -> list[res.Response]:
    """Batch `git init` command."""
    return _call_git_use_case("init", args)


@main.command(context_settings={"ignore_unknown_options": True})
@click.argument("args", nargs=-1)
def merge(args: tuple[str]) -> list[res.Response]:
    """Batch `git merge` command."""
    return _call_git_use_case("merge", args)


@main.command(context_settings={"ignore_unknown_options": True})
@click.argument("args", nargs=-1)
def mv(args: tuple[str]) -> list[res.Response]:
    """Batch `git mv` command."""
    return _call_git_use_case("mv", args)


@main.command(context_settings={"ignore_unknown_options": True})
@click.argument("args", nargs=-1)
def pull(args: tuple[str]) -> list[res.Response]:
    """Batch `git pull` command."""
    return _call_git_use_case("pull", args)


@main.command(context_settings={"ignore_unknown_options": True})
@click.argument("args", nargs=-1)
def push(args: tuple[str]) -> list[res.Response]:
    """Batch `git push` command."""
    return _call_git_use_case("push", args)


@main.command(context_settings={"ignore_unknown_options": True})
@click.argument("args", nargs=-1)
def rebase(args: tuple[str]) -> list[res.Response]:
    """Batch `git rebase` command."""
    return _call_git_use_case("rebase", args)


@main.command(context_settings={"ignore_unknown_options": True})
@click.argument("args", nargs=-1)
def reset(args: tuple[str]) -> list[res.Response]:
    """Batch `git reset` command."""
    return _call_git_use_case("reset", args)


@main.command(context_settings={"ignore_unknown_options": True})
@click.argument("args", nargs=-1)
def rm(args: tuple[str]) -> list[res.Response]:
    """Batch `git rm` command."""
    return _call_git_use_case("rm", args)


@main.command(context_settings={"ignore_unknown_options": True})
@click.argument("args", nargs=-1)
def show(args: tuple[str]) -> list[res.Response]:
    """Batch `git show` command."""
    return _call_git_use_case("show", args)


@main.command(context_settings={"ignore_unknown_options": True})
@click.argument("args", nargs=-1)
def status(args: tuple[str]) -> list[res.Response]:
    """Batch `git status` command."""
    return _call_git_use_case("status", args)


@main.command(context_settings={"ignore_unknown_options": True})
@click.argument("args", nargs=-1)
def switch(args: tuple[str]) -> list[res.Response]:
    """Batch `git switch` command."""
    return _call_git_use_case("switch", args)


@main.command(context_settings={"ignore_unknown_options": True})
@click.argument("args", nargs=-1)
def tag(args: tuple[str]) -> list[res.Response]:
    """Batch `git tag` command."""
    return _call_git_use_case("tag", args)


@click.group("config")
def group_config() -> None:
    """Config command group."""
    pass


@click.group("branches")
def group_branches() -> None:
    """Branches command group."""
    pass


@click.group("issues")
def group_issues() -> None:
    """Issues command group."""
    pass


@click.group("prs")
def group_prs() -> None:
    """Pull requests command group."""
    pass


@group_config.command("init")
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
            failure = cast(res.ResponseFailure, response)
            click.secho(f"Error: {failure.value['message']}", fg="red")
            if failure.type == res.ResponseTypes.SYSTEM_ERROR:
                click.ClickException("")


@group_config.command("repos")
@gitp_config_check
def config_repos() -> list[res.Response]:
    """Configure current working `gitp` repositories."""
    new_repos = p.InquirerPrompter.new_repos(
        CONFIG_MANAGER.config.github_selected_repos
    )
    if not new_repos:
        return [res.ResponseSuccess()]
    settings = _get_connection_settings(CONFIG_MANAGER.config)
    try:
        github_service = ghs.GithubService(settings)
    except ghs.GithubServiceError as gse:
        return [res.ResponseFailure(res.ResponseTypes.RESOURCE_ERROR, gse)]

    repo_names = github_service.get_repo_names()
    selected_repos = p.InquirerPrompter.select_repos(repo_names)
    return [
        cr.ConfigReposUseCase(CONFIG_MANAGER).execute(
            github_service.get_config(), selected_repos
        )
    ]


@group_issues.command("create")
@gitp_config_check
def create_issues() -> list[res.Response]:
    """Batch creation of issues on GitHub."""
    settings = _get_connection_settings(CONFIG_MANAGER.config)
    try:
        github_service = ghs.GithubService(settings)
    except ghs.GithubServiceError as gse:
        return [res.ResponseFailure(res.ResponseTypes.RESOURCE_ERROR, gse)]

    issue = p.InquirerPrompter.create_issues(
        CONFIG_MANAGER.config.github_selected_repos
    )
    return ghci.GhCreateIssueUseCase(CONFIG_MANAGER, github_service).execute(issue)


@group_issues.command("close")
@gitp_config_check
def close_issues() -> list[res.Response]:
    """Batch close issues on GitHub."""
    settings = _get_connection_settings(CONFIG_MANAGER.config)
    try:
        github_service = ghs.GithubService(settings)
    except ghs.GithubServiceError as gse:
        return [res.ResponseFailure(res.ResponseTypes.RESOURCE_ERROR, gse)]

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


@group_issues.command("reopen")
@gitp_config_check
def reopen_issues() -> list[res.Response]:
    """Batch reopen issues on GitHub."""
    settings = _get_connection_settings(CONFIG_MANAGER.config)
    try:
        github_service = ghs.GithubService(settings)
    except ghs.GithubServiceError as gse:
        return [res.ResponseFailure(res.ResponseTypes.RESOURCE_ERROR, gse)]

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
def poetry_cmd(args: tuple[str]) -> list[res.Response]:
    """Batch `poetry` command."""
    return poetry.PoetryUseCase().execute(
        CONFIG_MANAGER.config.github_selected_repos, "poetry", args
    )


@group_prs.command("create")
@gitp_config_check
def create_prs() -> list[res.Response]:
    """Batch creation of pull requests on GitHub."""
    settings = _get_connection_settings(CONFIG_MANAGER.config)
    try:
        github_service = ghs.GithubService(settings)
    except ghs.GithubServiceError as gse:
        return [res.ResponseFailure(res.ResponseTypes.RESOURCE_ERROR, gse)]

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


@group_prs.command("close")
@gitp_config_check
def close_prs() -> list[res.Response]:
    """Batch close pull requests on GitHub."""
    settings = _get_connection_settings(CONFIG_MANAGER.config)
    try:
        github_service = ghs.GithubService(settings)
    except ghs.GithubServiceError as gse:
        return [res.ResponseFailure(res.ResponseTypes.RESOURCE_ERROR, gse)]

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


@group_prs.command("merge")
@gitp_config_check
def merge_prs() -> list[res.Response]:
    """Batch merge of pull requests on GitHub."""
    settings = _get_connection_settings(CONFIG_MANAGER.config)
    try:
        github_service = ghs.GithubService(settings)
    except ghs.GithubServiceError as gse:
        return [res.ResponseFailure(res.ResponseTypes.RESOURCE_ERROR, gse)]

    pr_merge = p.InquirerPrompter.merge_pull_requests(
        github_service.get_username(),
        CONFIG_MANAGER.config.github_selected_repos,
    )
    return ghmp.GhMergePrUseCase(CONFIG_MANAGER, github_service).execute(pr_merge)


@group_branches.command("delete")
@gitp_config_check
def delete_branches() -> list[res.Response]:
    """Batch deletion of branches on GitHub."""
    settings = _get_connection_settings(CONFIG_MANAGER.config)
    try:
        github_service = ghs.GithubService(settings)
    except ghs.GithubServiceError as gse:
        return [res.ResponseFailure(res.ResponseTypes.RESOURCE_ERROR, gse)]

    branch = p.InquirerPrompter.delete_branches(
        CONFIG_MANAGER.config.github_selected_repos
    )
    return ghdb.GhDeleteBranchUseCase(CONFIG_MANAGER, github_service).execute(branch)


main.add_command(group_config)
main.add_command(group_branches)
main.add_command(group_issues)
main.add_command(group_prs)


if __name__ == "__main__":
    main(prog_name="gitp")  # pragma: no cover
