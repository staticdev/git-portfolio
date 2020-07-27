"""Command-line interface."""
import click

import git_portfolio.portfolio_manager as pm


@click.group("cli")
def cli() -> None:
    """Cli command group."""
    pass


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


cli.add_command(configure)
cli.add_command(create)
# cli.add_command(close)
cli.add_command(merge)
cli.add_command(delete)


def main(prog_name: str) -> None:
    """Git Portfolio."""
    cli()


if __name__ == "__main__":
    main(prog_name="gitp")  # pragma: no cover
