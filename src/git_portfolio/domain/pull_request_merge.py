"""Pull request merge model."""
import collections


PullRequestMerge = collections.namedtuple(
    "PullRequestMerge", ["base", "head", "prefix", "delete_branch"]
)
