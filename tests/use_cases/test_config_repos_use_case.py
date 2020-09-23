"""Test cases for the gitp repositories config use case."""
import pytest
from pytest_mock import MockerFixture

import git_portfolio.domain.config as c
import git_portfolio.use_cases.config_repos_use_case as cr


@pytest.fixture
def mock_config_manager(mocker: MockerFixture) -> MockerFixture:
    """Fixture for mocking ConfigManager."""
    mock = mocker.patch("git_portfolio.config_manager.ConfigManager", autospec=True)
    return mock


def test_execute(mock_config_manager: MockerFixture) -> None:
    """It returns success."""
    config_manager = mock_config_manager.return_value
    config_manager.config = c.Config("", "abc", [])
    response = cr.ConfigReposUseCase(config_manager).execute(["staticdev/omg"])

    assert bool(response) is True
    assert "gitp repositories successfully configured." == response.value
