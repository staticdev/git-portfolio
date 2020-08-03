"""Configuration manager module."""
import os
import pathlib
from typing import List

import yaml


class Config:
    """Config class."""

    def __init__(
        self,
        github_hostname: str,
        github_access_token: str,
        github_selected_repos: List[str],
    ):
        """Constructor."""
        self.github_hostname = github_hostname
        self.github_access_token = github_access_token
        self.github_selected_repos = github_selected_repos


class ConfigManager:
    """Configuration manager class."""

    CONFIG_FOLDER = os.path.join(os.path.expanduser("~"), ".gitp")
    CONFIG_FILE = "config.yaml"

    def load_configs(self) -> Config:
        """Get configs if it exists."""
        if os.path.exists(os.path.join(self.CONFIG_FOLDER, self.CONFIG_FILE)):
            print("Loading previous configs\n")
            with open(
                os.path.join(self.CONFIG_FOLDER, self.CONFIG_FILE)
            ) as config_file:
                data = yaml.safe_load(config_file)
                return Config(**data)
        return Config("", "", [])

    def save_configs(self, configs: Config) -> None:
        """Write config to YAML file."""
        pathlib.Path(self.CONFIG_FOLDER).mkdir(parents=True, exist_ok=True)
        configs_dict = vars(configs)
        with open(
            os.path.join(self.CONFIG_FOLDER, self.CONFIG_FILE), "w"
        ) as config_file:
            yaml.dump(configs_dict, config_file)
