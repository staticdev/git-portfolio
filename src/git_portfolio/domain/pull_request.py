"""Pull request model."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PullRequest:
    """Pull request class."""

    title: str
    body: str
    labels: set[str]
    link_issues: bool
    issues_title_query: str
    inherit_labels: bool
    head: str
    base: str
    draft: bool
