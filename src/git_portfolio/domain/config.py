"""Config model."""
from dataclasses import dataclass
from typing import List


@dataclass
class Config:
    """Configuration class."""

    github_hostname: str
    github_access_token: str
    github_selected_repos: List[str]
