"""Command-line interface."""
from typing import Tuple

import click

import git_portfolio.config_manager as cm
import git_portfolio.local_manager as lm
import git_portfolio.portfolio_manager as pm


@click.group("cli")
def main() -> None:
    """Git Portfolio."""
    pass


@main.command("checkout")
@click.argument("args", nargs=-1)
def checkout(args: Tuple[str]) -> None:
    """CLI `git checkout BRANCH` command."""
    # TODO add -b option
    config_manager = cm.ConfigManager()
    configs = config_manager.load_configs()
    if not configs.github_selected_repos:
        click.secho(
            "Error: no repos selected. Please run `gitp config init`.", fg="red",
        )
    elif len(args) != 1:
        click.secho(
            (
                "Error: please put exactly one argument after checkout, eg.: "
                "`gitp checkout BRANCH`."
            ),
            fg="red",
        )
    else:
        click.secho(lm.LocalManager().checkout(configs.github_selected_repos, args))


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


@configure.command("init")
def config_init() -> None:
    """Config init command."""
    pm.PortfolioManager()


@configure.command("repos")
def config_repos() -> None:
    """Config repos command."""
    pm.PortfolioManager().config_repos()


@create.command("issues")
def create_issues() -> None:
    """Create issues command."""
    pm.PortfolioManager().create_issues()


@create.command("prs")
def create_prs() -> None:
    """Create prs command."""
    pm.PortfolioManager().create_pull_requests()


@merge.command("prs")
def merge_prs() -> None:
    """Merge prs command."""
    pm.PortfolioManager().merge_pull_requests()


@delete.command("branches")
def delete_branches() -> None:
    """Delete branches command."""
    pm.PortfolioManager().delete_branches()


main.add_command(configure)
main.add_command(create)
# main.add_command(close)
main.add_command(merge)
main.add_command(delete)


if __name__ == "__main__":
    main(prog_name="gitp")  # pragma: no cover
