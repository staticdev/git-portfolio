"""Pull request model."""
import collections

PullRequest = collections.namedtuple(
    "PullRequest",
    [
        "title",
        "body",
        "labels",
        "confirmation",
        "link",
        "inherit_labels",
        "head",
        "base",
        "draft",
    ],
)
