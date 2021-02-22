"""Test cases for the config manager module."""
import pathlib

import pytest
from pytest_mock import MockerFixture

from git_portfolio import config_manager as cm


@pytest.fixture
def mock_os_join_path(mocker: MockerFixture) -> MockerFixture:
    """Fixture for mocking os.path.join."""
    return mocker.patch("os.path.join")


@pytest.fixture
def mock_yaml_dump(mocker: MockerFixture) -> MockerFixture:
    """Fixture for mocking yaml.dump."""
    return mocker.patch("yaml.dump")


def test_init_invalid_config(
    tmp_path: pathlib.Path, mock_os_join_path: MockerFixture
) -> None:
    """It trucantes the file."""
    filename = "config1.yaml"
    d = tmp_path
    p = d / filename
    p.write_text("in:valid")
    mock_os_join_path.side_effect = [str(d), str(p)]
    cm.ConfigManager()
    # os_truncate.assert_called_once_with(0)


def test_save_invalid_yaml(
    tmp_path: pathlib.Path, mock_os_join_path: MockerFixture
) -> None:
    """It trucantes the file."""
    filename = "config.yaml"
    content = (
        "github_access_token: aaaaabbbbbccccc12345"
        "github_hostname: ''"
        "github_selected_repos:"
        " - staticdev/test"
    )
    d = tmp_path
    p = d / filename
    p.write_text(content)
    mock_os_join_path.side_effect = [str(d), str(p)]
    cm.ConfigManager()
    # os_truncate.assert_called_once_with(0)


def test_save_config_no_file(
    tmp_path: pathlib.Path, mock_os_join_path: MockerFixture
) -> None:
    """It raises AttributeError."""
    d = tmp_path
    mock_os_join_path.side_effect = [str(d), str(d / "config.yaml")]
    manager = cm.ConfigManager()
    with pytest.raises(AttributeError):
        manager.save_config()


def test_save_config_empty_file(
    tmp_path: pathlib.Path, mock_os_join_path: MockerFixture
) -> None:
    """It raises AttributeError."""
    filename = "config2.yaml"
    d = tmp_path
    p = d / filename
    p.write_text("")
    mock_os_join_path.side_effect = [str(d), str(p)]
    manager = cm.ConfigManager(filename)
    with pytest.raises(AttributeError):
        manager.save_config()


def test_save_config_success(
    tmp_path: pathlib.Path,
    mock_yaml_dump: MockerFixture,
    mock_os_join_path: MockerFixture,
) -> None:
    """It dumps yaml config file."""
    filename = "config.yaml"
    content = (
        "github_access_token: aaaaabbbbbccccc12345\n"
        "github_hostname: ''\n"
        "github_selected_repos:\n"
        " - staticdev/test\n"
    )
    d = tmp_path
    p = d / filename
    p.write_text(content)
    mock_os_join_path.side_effect = [str(d), str(p)]
    manager = cm.ConfigManager()
    manager.save_config()
    mock_yaml_dump.assert_called_once()
