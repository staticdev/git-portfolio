"""Config model."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Config:
    """Configuration class."""

    github_hostname: str
    github_access_token: str
    github_selected_repos: list[str]
