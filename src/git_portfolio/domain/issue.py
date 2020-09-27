"""Issue model."""
from dataclasses import dataclass
from typing import Set


@dataclass
class Issue:
    """Issue class."""

    title: str
    body: str
    labels: Set[str]
