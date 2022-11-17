"""Test cases for the repositories config use case."""
import pytest
from pytest_mock import MockerFixture

import git_portfolio.domain.config as c
import git_portfolio.domain.gh_connection_settings as cs
import git_portfolio.responses as res
import git_portfolio.use_cases.config_repos as cr
from tests.conftest import CLI_COMMAND


@pytest.fixture
def domain_gh_conn_settings() -> cs.GhConnectionSettings:
    """Github connection settings fixture."""
    return cs.GhConnectionSettings(
        "my-token",
        "myhost.com",
    )


@pytest.fixture
def mock_config_manager(mocker: MockerFixture) -> MockerFixture:
    """Fixture for mocking ConfigManager."""
    mock = mocker.patch("git_portfolio.config_manager.ConfigManager", autospec=True)
    return mock


def test_execute(
    domain_gh_conn_settings: cs.GhConnectionSettings, mock_config_manager: MockerFixture
) -> None:
    """It returns success."""
    config_manager = mock_config_manager.return_value
    config_manager.config = c.Config("", "abc", [])
    response = cr.ConfigReposUseCase(config_manager).execute(
        domain_gh_conn_settings, ["user/repo"]
    )

    assert isinstance(response, res.ResponseSuccess)
    assert response.value == f"{CLI_COMMAND} repositories successfully configured."
