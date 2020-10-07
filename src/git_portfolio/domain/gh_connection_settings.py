"""Github connection settings model."""
from dataclasses import dataclass


@dataclass
class GhConnectionSettings:
    """Github connection settings class."""

    access_token: str
    hostname: str
