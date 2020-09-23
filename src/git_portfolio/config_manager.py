"""Configuration manager module."""
import os
import pathlib

import yaml

import git_portfolio.domain.config as c


class ConfigManager:
    """Configuration manager class."""

    def __init__(self, config_filename: str = "config.yaml") -> None:
        """Load config if it exists."""
        self.config_folder = os.path.join(os.path.expanduser("~"), ".gitp")
        self.config_path = os.path.join(self.config_folder, config_filename)

        if os.path.exists(self.config_path):
            print("Loading previous config...\n")
            with open(self.config_path, "r+") as config_file:
                try:
                    data = yaml.safe_load(config_file)
                    if data:
                        try:
                            self.config = c.Config(**data)
                            return
                        except TypeError:
                            config_file.truncate(0)
                except yaml.scanner.ScannerError:
                    config_file.truncate(0)
        self.config = c.Config("", "", [])

    def config_is_empty(self) -> bool:
        """Check if config is empty."""
        if self.config.github_selected_repos and self.config.github_access_token:
            return False
        return True

    def save_config(self) -> None:
        """Write config to YAML file."""
        if not self.config_is_empty():
            pathlib.Path(self.config_folder).mkdir(parents=True, exist_ok=True)
            config_dict = vars(self.config)
            with open(self.config_path, "w") as config_file:
                yaml.dump(config_dict, config_file)
        else:
            raise AttributeError
