"""Test cases for the Github pull request model."""
import git_portfolio.domain.pull_request as pr


def test_pr_model_init() -> None:
    """Verify model initialization."""
    title = "issue title"
    body = "body description"
    labels = {"testing"}
    link_issues = True
    link = ""
    inherit = True
    head = "master"
    base = "node"
    draft = False
    test_pr = pr.PullRequest(
        title, body, labels, link_issues, link, inherit, head, base, draft
    )

    assert test_pr.title == title
    assert test_pr.body == body
    assert test_pr.labels == labels
    assert test_pr.link_issues == link_issues
    assert test_pr.link == link
    assert test_pr.inherit_labels == inherit
    assert test_pr.head == head
    assert test_pr.base == base
    assert test_pr.draft == draft
