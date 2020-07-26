"""Test cases for the __main__ module."""
import pytest
from click.testing import CliRunner

from git_portfolio import __main__


@pytest.fixture
def runner() -> CliRunner:
    """Fixture for invoking command-line interfaces."""
    return CliRunner()


def test_main_without_argument(runner: CliRunner) -> None:
    """It exits with a status code of one."""
    result = runner.invoke(__main__.main, prog_name="gitp")
    assert result.exit_code == 1
