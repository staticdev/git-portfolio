"""Test cases for response objects."""
from typing import Dict
from typing import List

import pytest

import git_portfolio.response_objects as res


@pytest.fixture
def response_value() -> Dict[str, List[str]]:
    """Fixture for response value."""
    return {"key": ["value1", "value2"]}


@pytest.fixture
def response_type() -> str:
    """Fixture for response type."""
    return "ResponseError"


@pytest.fixture
def response_message() -> str:
    """Fixture for response message."""
    return "This is a response error"


def test_response_success_is_true(response_value: Dict[str, List[str]]) -> None:
    """It has bool value of True."""
    assert bool(res.ResponseSuccess(response_value)) is True


def test_response_success_has_type_and_value(
    response_value: Dict[str, List[str]]
) -> None:
    """It has success type and value."""
    response = res.ResponseSuccess(response_value)

    assert response.type == res.ResponseSuccess.SUCCESS
    assert response.value == response_value


def test_response_failure_is_false(response_type: str, response_message: str) -> None:
    """It has bool value of False."""
    assert bool(res.ResponseFailure(response_type, response_message)) is False


def test_response_failure_has_type_and_message(
    response_type: str, response_message: str
) -> None:
    """It has failure type and message."""
    response = res.ResponseFailure(response_type, response_message)

    assert response.type == response_type
    assert response.message == response_message


def test_response_failure_contains_value(
    response_type: str, response_message: str
) -> None:
    """It has response type and message."""
    response = res.ResponseFailure(response_type, response_message)

    assert response.value == {"type": response_type, "message": response_message}


def test_response_failure_initialisation_with_exception(response_type: str) -> None:
    """It builds a ResponseFailure from exception."""
    response = res.ResponseFailure(response_type, Exception("Just an error message"))

    assert bool(response) is False
    assert response.type == response_type
    assert response.message == "Exception: Just an error message"


def test_response_failure_build_resource_error() -> None:
    """It builds a ResponseFailure with type resource error."""
    response = res.ResponseFailure.build_resource_error("test message")

    assert bool(response) is False
    assert response.type == res.ResponseFailure.RESOURCE_ERROR
    assert response.message == "test message"


def test_response_failure_build_parameters_error() -> None:
    """It builds a ResponseFailure with type parameters error."""
    response = res.ResponseFailure.build_parameters_error("test message")

    assert bool(response) is False
    assert response.type == res.ResponseFailure.PARAMETERS_ERROR
    assert response.message == "test message"


def test_response_failure_build_system_error() -> None:
    """It builds a ResponseFailure with type system error."""
    response = res.ResponseFailure.build_system_error("test message")

    assert bool(response) is False
    assert response.type == res.ResponseFailure.SYSTEM_ERROR
    assert response.message == "test message"
