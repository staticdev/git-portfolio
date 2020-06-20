import collections
import os
import yaml
from typing import List


class Config:
    def __init__(self, github_access_token: str = "", github_selected_repos: List[str] = [""]):
        self.github_access_token = github_access_token
        self.github_selected_repos = github_selected_repos


class ConfigManager:
    CONFIG_FOLDER = os.path.join(os.path.expanduser("~"), ".gitp")
    CONFIG_FILE = "config.yaml"

    def load_configs(self) -> Config:
        if os.path.exists(os.path.join(self.CONFIG_FOLDER, self.CONFIG_FILE)):
            print("Loading previous configs\n")
            with open(os.path.join(self.CONFIG_FOLDER, self.CONFIG_FILE)) as config_file:
                data = yaml.load(config_file)
                return Config(**data)
        os.system(f"mkdir -p {self.CONFIG_FOLDER}")
        return Config()

    def save_configs(self, configs: Config):
        configs_dict = vars(configs)
        with open(
            os.path.join(self.CONFIG_FOLDER, self.CONFIG_FILE), "w"
        ) as config_file:
            yaml.dump(configs_dict, config_file)
