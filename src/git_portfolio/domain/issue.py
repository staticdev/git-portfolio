"""Issue model."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Issue:
    """Issue class."""

    number: int
    title: str
    body: str
    labels: set[str]
