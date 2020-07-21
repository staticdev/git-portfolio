"""Command-line interface."""
import click

import git_portfolio.portfolio_manager as pm


@click.group("cli")
def cli():
    pass


@click.group("config")
def configure():
    pass


@click.group("create")
def create():
    pass


@click.group("merge")
def merge():
    pass


# TODO
# @click.group("close")
# def close():
#     pass


@click.group("delete")
def delete():
    pass


@configure.command("init")
def config_init():
    pm.PortfolioManager()


@configure.command("repos")
def config_repos():
    pm.PortfolioManager().config_repos()


@create.command("issues")
def create_issues():
    pm.PortfolioManager().create_issues()


@create.command("prs")
def create_prs():
    pm.PortfolioManager().create_pull_requests()


@merge.command("prs")
def merge_prs():
    pm.PortfolioManager().merge_pull_requests()


@delete.command("branches")
def delete_branches():
    pm.PortfolioManager().delete_branches()


cli.add_command(configure)
cli.add_command(create)
# cli.add_command(close)
cli.add_command(merge)
cli.add_command(delete)


def main() -> None:
    """Git Portfolio."""
    cli()


if __name__ == "__main__":
    # main(prog_name="gitp")  # pragma: no cover
    pm.PortfolioManager().config_repos()
