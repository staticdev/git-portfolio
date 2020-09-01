"""Command-line interface."""
import functools
from typing import Any
from typing import Callable
from typing import cast
from typing import Tuple
from typing import TypeVar
from typing import Union

import click

import git_portfolio.config_manager as cm
import git_portfolio.git_use_case as guc
import git_portfolio.github_manager as ghm
import git_portfolio.response_objects as res

F = TypeVar("F", bound=Callable[..., Any])
CONFIG_MANAGER = cm.ConfigManager()


def git_command(func: F) -> F:
    """Validate if there are selected repos and outputs success."""

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        if not CONFIG_MANAGER.config.github_selected_repos:
            click.secho(
                "Error: no repos selected. Please run `gitp config init`.",
                fg="red",
            )
        else:
            value = func(*args, **kwargs)
            _echo_outputs(value)
            return value

    return cast(F, wrapper)


@click.group("cli")
def main() -> None:
    """Git Portfolio."""
    pass


def _echo_outputs(response: Union[res.ResponseFailure, res.ResponseSuccess]) -> None:
    if bool(response):
        success = cast(res.ResponseSuccess, response)
        click.secho(success.value)
    else:
        click.secho(f"Error: {response.value['message']}", fg="red")


@main.command("checkout")
@click.argument("args", nargs=-1)
@git_command
def checkout(args: Tuple[str]) -> Union[res.ResponseFailure, res.ResponseSuccess]:
    """CLI `git checkout BRANCH` command."""
    return guc.GitUseCase().execute(
        CONFIG_MANAGER.config.github_selected_repos, "checkout", args
    )


@main.command("pull")
@click.argument("args", nargs=-1)
@git_command
def pull(args: Tuple[str]) -> Union[res.ResponseFailure, res.ResponseSuccess]:
    """CLI `git pull` command."""
    return guc.GitUseCase().execute(
        CONFIG_MANAGER.config.github_selected_repos, "pull", args
    )


@main.command("push")
@click.argument("args", nargs=-1)
@git_command
def push(args: Tuple[str]) -> Union[res.ResponseFailure, res.ResponseSuccess]:
    """CLI `git push` command."""
    return guc.GitUseCase().execute(
        CONFIG_MANAGER.config.github_selected_repos, "push", args
    )


@main.command("status")
@click.argument("args", nargs=-1)
@git_command
def status(args: Tuple[str]) -> Union[res.ResponseFailure, res.ResponseSuccess]:
    """CLI `git status` command."""
    return guc.GitUseCase().execute(
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


# TODO
# @click.group("close")
# def close() -> None:
#     """Close command group."""
#     pass


@click.group("delete")
def delete() -> None:
    """Delete command group."""
    pass


def _save_config(config: cm.Config) -> None:
    """Save config with ConfigManager."""
    CONFIG_MANAGER.config = config
    CONFIG_MANAGER.save_config()
    click.secho("gitp successfully configured.", fg="blue")


@configure.command("init")
def config_init() -> None:
    """Config init command."""
    github_manager = ghm.GithubManager(CONFIG_MANAGER.config)
    _save_config(github_manager.config)


@configure.command("repos")
def config_repos() -> None:
    """Config repos command."""
    if CONFIG_MANAGER.config_is_empty():
        click.secho("Error: no config found, please run `gitp config init`.", fg="red")
    else:
        config = ghm.GithubManager(CONFIG_MANAGER.config).config_repos()
        if config:
            _save_config(config)


@create.command("issues")
def create_issues() -> None:
    """Create issues command."""
    ghm.GithubManager(CONFIG_MANAGER.config).create_issues()


@create.command("prs")
def create_prs() -> None:
    """Create prs command."""
    ghm.GithubManager(CONFIG_MANAGER.config).create_pull_requests()


@merge.command("prs")
def merge_prs() -> None:
    """Merge prs command."""
    ghm.GithubManager(CONFIG_MANAGER.config).merge_pull_requests()


@delete.command("branches")
def delete_branches() -> None:
    """Delete branches command."""
    ghm.GithubManager(CONFIG_MANAGER.config).delete_branches()


main.add_command(configure)
main.add_command(create)
# main.add_command(close)
main.add_command(merge)
main.add_command(delete)


if __name__ == "__main__":
    main(prog_name="gitp")  # pragma: no cover
