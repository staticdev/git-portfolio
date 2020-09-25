"""Test cases for the Github merge PR use case."""
# from typing import List
# from unittest.mock import Mock
# import pytest
# from pytest_mock import MockerFixture
# import git_portfolio.domain.config as c
# import git_portfolio.domain.pull_request_merge as mpr
# import git_portfolio.use_cases.gh_merge_pr_use_case as ghmp
# # TODO: scenarios is coupled with get_pull
# @pytest.fixture
# def mock_github_manager(mocker: MockerFixture) -> MockerFixture:
#     """Fixture for mocking GithubManager."""
#     mock = mocker.patch("git_portfolio.github_manager.GithubManager", autospec=True)
#     mock.return_value.config = c.Config("", "mytoken", ["staticdev/omg"])
#     mock.return_value.github_connection = Mock()
#     return mock
# @pytest.fixture
# def domain_mprs() -> List[mpr.PullRequestMerge]:
#     """Pull request merge fixture."""
#     mprs = [
#         mpr.PullRequestMerge(
#             "branch", "main", "org name", False
#         ),
#         mpr.PullRequestMerge(
#             "branch-2", "main", "org name", True
#         ),
#     ]
#     return mprs
# def test_execute_for_all_repos(
#     mock_github_manager: MockerFixture, domain_mprs: List[mpr.PullRequestMerge]
# ) -> None:
#     """It returns success."""
#     github_manager = mock_github_manager.return_value
#     response = ghmp.GhMergePrUseCase(github_manager).execute(domain_mprs[0])
#     assert bool(response) is True
#     assert "staticdev/omg: PR merged successfully." == response.value
# def test_execute_for_specific_repo(
#     mock_github_manager: MockerFixture, domain_mprs: List[mpr.PullRequestMerge]
# ) -> None:
#     """It returns success."""
#     github_manager = mock_github_manager.return_value
#     response = ghmp.GhMergePrUseCase(github_manager).execute(
#         domain_mprs[0], "staticdev/omg"
#     )
#     assert bool(response) is True
#     assert "staticdev/omg: PR merged successfully." == response.value
# def test_execute_delete_branch(
#     mock_github_manager: MockerFixture, domain_mprs: List[mpr.PullRequestMerge]
# ) -> None:
#     """It returns success."""
#     github_manager = mock_github_manager.return_value
#     response = ghmp.GhMergePrUseCase(github_manager).execute(
#         domain_mprs[1], "staticdev/omg"
#     )
#     assert bool(response) is True
#     assert "staticdev/omg: PR merged successfully." == response.value
