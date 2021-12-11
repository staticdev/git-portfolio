"""Package-wide test fixtures."""
import _pytest.config

import git_portfolio.domain.issue as i
import git_portfolio.domain.pull_request as pr
import git_portfolio.domain.pull_request_merge as mpr


def pytest_configure(config: _pytest.config.Config) -> None:
    """Pytest configuration hook."""
    config.addinivalue_line("markers", "e2e: mark as end-to-end test.")
    config.addinivalue_line("markers", "integration: mark as integration test.")


CLI_COMMAND = "gitp"
REPO_NAME = "repo-name"
REPO = f"org/{REPO_NAME}"
REPO2 = f"org/{REPO_NAME}2"
SUCCESS_MSG = f"{REPO}: success output"
ERROR_MSG = "some error"
LABEL_BUG = "bug"
LABEL_ENHANCEMENT = "enhancement"
LABEL_DO_NOT_INHERIT = "do_not_use"
DOMAIN_ISSUES = [
    i.Issue(0, "my issue title", "issue body", {LABEL_BUG}),
    i.Issue(1, "doesnt match title", "body4", {LABEL_DO_NOT_INHERIT}),
    i.Issue(2, "issue title", "body3", set()),
    i.Issue(3, "pr match issue title", "body5", {LABEL_ENHANCEMENT}),
]
DOMAIN_PRS = [
    pr.PullRequest(
        "my pr title",
        "my pr body",
        set(),
        False,
        "",
        False,
        "main",
        "branch",
        False,
    ),
    pr.PullRequest(
        "my pr title 2",
        "my pr body 2",
        {LABEL_BUG, LABEL_BUG},
        True,
        "issue title",
        True,
        "main",
        "branch",
        False,
    ),
]
DOMAIN_MPR = mpr.PullRequestMerge("branch", "main", "org name", False)
BRANCH_NAME = "my-branch"
