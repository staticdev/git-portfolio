"""Github connection settings model."""
from dataclasses import dataclass


@dataclass
class GhConnectionSettings:
    """Github connection settings class."""

    github_access_token: str
    github_hostname: str
