"""Command-line interface."""
from typing import Tuple

import click

import git_portfolio.config_manager as cm
import git_portfolio.git_command as gc
import git_portfolio.github_manager as ghm


CONFIG_MANAGER = cm.ConfigManager()


@click.group("cli")
def main() -> None:
    """Git Portfolio."""
    pass


def _echo_outputs(output: str, error: str) -> None:
    if error:
        click.secho(error, fg="red")
    else:
        click.secho(output)


@main.command("checkout")
@click.argument("args", nargs=-1)
def checkout(args: Tuple[str]) -> None:
    """CLI `git checkout BRANCH` command."""
    max_args = 2
    if not CONFIG_MANAGER.config.github_selected_repos:
        click.secho(
            "Error: no repos selected. Please run `gitp config init`.", fg="red",
        )
    elif len(args) > max_args:
        click.secho(
            (
                "Error: please provide maximum of {max_args} arguments after checkout,"
                " eg.: `gitp checkout BRANCH`."
            ),
            fg="red",
        )
    else:
        stdout, err = gc.GitCommand().execute(
            CONFIG_MANAGER.config.github_selected_repos, "checkout", args
        )
        _echo_outputs(stdout, err)


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
