"""Test cases for the issue list requests."""
from typing import cast
import pytest

import git_portfolio.request_objects.issue_list as il


def test_build_list_request_without_parameters() -> None:
    """It returns valid request with no filters."""
    request = cast(il.IssueListValidRequest, il.build_list_request())

    assert request.filters is None
    assert bool(request) is True


def test_build_list_request_with_empty_filters() -> None:
    """It returns valid request with no filters."""
    request = cast(il.IssueListValidRequest, il.build_list_request(filters={}))

    assert request.filters == {}
    assert bool(request) is True


def test_build_list_request_with_incorrect_filter_keys() -> None:
    """It returns invalid request."""
    request = cast(
        il.IssueListInvalidRequest, il.build_list_request(filters={"a": "1"})
    )

    assert request.has_errors()
    assert request.errors[0]["parameter"] == "filters"
    assert bool(request) is False


@pytest.mark.parametrize("key", ["obj__eq", "state__eq", "title__contains"])
def test_build_list_request_accepted_filters(key: str) -> None:
    """It returns valid request."""
    filters = {key: "all"}

    request = cast(il.IssueListValidRequest, il.build_list_request(filters=filters))

    assert request.filters == filters
    assert bool(request) is True


@pytest.mark.parametrize("key", ["state__lt", "title__eq"])
def test_build_list_request_rejected_filters(key: str) -> None:
    """It returns invalid request."""
    filters = {key: "1"}

    request = cast(il.IssueListInvalidRequest, il.build_list_request(filters=filters))

    assert request.has_errors()
    assert request.errors[0]["parameter"] == "filters"
    assert bool(request) is False


@pytest.mark.parametrize("value", ["issue", "pull request", "all"])
def test_build_list_request_accepted_obj_values(value: str) -> None:
    """It returns valid request."""
    filters = {"obj__eq": value}

    request = cast(il.IssueListValidRequest, il.build_list_request(filters=filters))

    assert request.filters == filters
    assert bool(request) is True


@pytest.mark.parametrize("value", ["all", "open", "closed"])
def test_build_list_request_accepted_state_values(value: str) -> None:
    """It returns valid request."""
    filters = {"state__eq": value}

    request = cast(il.IssueListValidRequest, il.build_list_request(filters=filters))

    assert request.filters == filters
    assert bool(request) is True


@pytest.mark.parametrize("value", ["mr", "a"])
def test_build_list_request_rejected_obj_values(value: str) -> None:
    """It returns invalid request."""
    filters = {"obj__eq": value}

    request = cast(il.IssueListInvalidRequest, il.build_list_request(filters=filters))

    assert request.has_errors()
    assert request.errors[0]["parameter"] == "filters"
    assert bool(request) is False


@pytest.mark.parametrize("value", ["close", "reopened"])
def test_build_list_request_rejected_state_values(value: str) -> None:
    """It returns invalid request."""
    filters = {"state__eq": value}

    request = cast(il.IssueListInvalidRequest, il.build_list_request(filters=filters))

    assert request.has_errors()
    assert request.errors[0]["parameter"] == "filters"
    assert bool(request) is False
