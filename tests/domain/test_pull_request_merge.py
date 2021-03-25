"""Test cases for the Github pull request merge model."""
import git_portfolio.domain.pull_request_merge as prm


def test_pr_model_init() -> None:
    """Verify model initialization."""
    head = "main"
    base = "node"
    prefix = "omg"
    delete = False
    test_prm = prm.PullRequestMerge(base, head, prefix, delete)

    assert test_prm.base == base
    assert test_prm.head == head
    assert test_prm.prefix == prefix
    assert test_prm.delete_branch == delete
