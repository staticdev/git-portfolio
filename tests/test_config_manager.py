"""Test cases for the config manager module."""
from unittest.mock import Mock
from unittest.mock import patch

import pytest

from git_portfolio import config_manager as cm


@patch("os.path.join")
class TestConfigManager:
    """ConfigManager test class."""

    def test_init_invalid_config(self, os_join_path: Mock, tmp_path: Mock) -> None:
        """It trucantes the file."""
        filename = "config1.yaml"
        d = tmp_path
        p = d / filename
        p.write_text("in:valid")
        os_join_path.side_effect = [str(d), str(p)]
        cm.ConfigManager()
        # os_truncate.assert_called_once_with(0)

    def test_save_invalid_yaml(self, os_join_path: Mock, tmp_path: Mock) -> None:
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
        os_join_path.side_effect = [str(d), str(p)]
        cm.ConfigManager()
        # os_truncate.assert_called_once_with(0)

    def test_save_config_no_file(self, os_join_path: Mock, tmp_path: Mock) -> None:
        """It raises AttributeError."""
        d = tmp_path
        os_join_path.side_effect = [str(d), str(d / "config.yaml")]
        manager = cm.ConfigManager()
        with pytest.raises(AttributeError):
            manager.save_config()

    def test_save_config_empty_file(self, os_join_path: Mock, tmp_path: Mock) -> None:
        """It raises AttributeError."""
        filename = "config2.yaml"
        d = tmp_path
        p = d / filename
        p.write_text("")
        os_join_path.side_effect = [str(d), str(p)]
        manager = cm.ConfigManager(filename)
        with pytest.raises(AttributeError):
            manager.save_config()

    @patch("yaml.dump")
    def test_save_config_success(
        self, yaml_dump: Mock, os_join_path: Mock, tmp_path: Mock
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
        os_join_path.side_effect = [str(d), str(p)]
        manager = cm.ConfigManager()
        manager.save_config()
        yaml_dump.assert_called_once()
