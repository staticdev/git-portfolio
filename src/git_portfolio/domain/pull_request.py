"""Pull request model."""
from dataclasses import dataclass
from typing import Set


@dataclass
class PullRequest:
    """Pull request class."""

    title: str
    body: str
    labels: Set[str]
    link_issues: bool
    link: str
    inherit_labels: bool
    head: str
    base: str
    draft: bool
