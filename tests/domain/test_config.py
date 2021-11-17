"""Test cases for config model."""
import git_portfolio.domain.config as c


def test_config_model_init() -> None:
    """Verify model initialization."""
    github_hostname = "localhost"
    github_access_token = "my-token"
    github_selected_repos = ["user/repo", "user/repo2"]
    test_config = c.Config(github_hostname, github_access_token, github_selected_repos)

    assert test_config.github_hostname == github_hostname
    assert test_config.github_access_token == github_access_token
    assert test_config.github_selected_repos == github_selected_repos
