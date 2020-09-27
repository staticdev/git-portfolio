"""Pull request merge model."""
from dataclasses import dataclass


@dataclass
class PullRequestMerge:
    """Pull request merge class."""

    base: str
    head: str
    prefix: str
    delete_branch: bool
