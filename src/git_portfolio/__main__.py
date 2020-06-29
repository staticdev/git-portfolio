"""Command-line interface."""
import click

import git_portfolio.github_manager as ghm


@click.group("cli")
def cli():
    pass


@click.group("init")
def init():
    pass


@click.group("create")
def create():
    pass


@click.group("merge")
def merge():
    pass


@click.group("close")
def close():
    pass


@click.group("delete")
def delete():
    pass


@create.command("issue")
def create_issues():
    ghm.GithubManager().create_issues()


@create.command("pr")
def create_prs():
    ghm.GithubManager().create_pull_requests()


@merge.command("pr")
def merge_prs():
    ghm.GithubManager().merge_pull_requests()


@delete.command("branch")
def delete_branches():
    ghm.GithubManager().delete_branches()


@init.command("config")
def config():
    ghm.GithubManager().init_config()


cli.add_command(init)
cli.add_command(create)
cli.add_command(close)
cli.add_command(merge)
cli.add_command(delete)


def main() -> None:
    """Git Portfolio."""
    cli()


if __name__ == "__main__":
    main(prog_name="gitp")  # pragma: no cover
