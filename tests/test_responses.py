"""Test cases for response objects."""
import git_portfolio.request_objects.issue_list as il
import git_portfolio.responses as res

SUCCESS_VALUE = {"key": ["value1", "value2"]}
GENERIC_RESPONSE_TYPE = "Response"
GENERIC_RESPONSE_MESSAGE = "This is a response"


def test_response_success_is_true() -> None:
    """It has bool value of True."""
    response = res.ResponseSuccess(SUCCESS_VALUE)

    assert bool(response) is True


def test_response_success_has_type_and_value() -> None:
    """It has success type and value."""
    response = res.ResponseSuccess(SUCCESS_VALUE)

    assert response.type == res.ResponseTypes.SUCCESS
    assert response.value == SUCCESS_VALUE


def test_response_failure_is_false() -> None:
    """It has bool value of False."""
    response = res.ResponseFailure(GENERIC_RESPONSE_TYPE, GENERIC_RESPONSE_MESSAGE)

    assert bool(response) is False


def test_response_failure_has_type_and_message() -> None:
    """It has failure type and message."""
    response = res.ResponseFailure(GENERIC_RESPONSE_TYPE, GENERIC_RESPONSE_MESSAGE)

    assert response.type == GENERIC_RESPONSE_TYPE
    assert response.message == GENERIC_RESPONSE_MESSAGE
    assert response.value == {
        "type": GENERIC_RESPONSE_TYPE,
        "message": GENERIC_RESPONSE_MESSAGE,
    }


def test_response_failure_initialisation_with_exception() -> None:
    """It builds a ResponseFailure from exception."""
    response = res.ResponseFailure(
        GENERIC_RESPONSE_TYPE, Exception("Just an error message")
    )

    assert bool(response) is False
    assert response.type == GENERIC_RESPONSE_TYPE
    assert response.message == "Exception: Just an error message"


def test_response_failure_from_empty_invalid_request() -> None:
    """It builds a ResponseFailure from empty request."""
    response = res.build_response_from_invalid_request(il.IssueListInvalidRequest())

    assert bool(response) is False
    assert response.type == res.ResponseTypes.PARAMETERS_ERROR


def test_response_failure_from_invalid_request_with_errors() -> None:
    """It builds a ResponseFailure from errors in invalid request."""
    request = il.IssueListInvalidRequest()
    request.add_error("path", "Is mandatory")
    request.add_error("path", "can't be blank")

    response = res.build_response_from_invalid_request(request)

    assert bool(response) is False
    assert response.type == res.ResponseTypes.PARAMETERS_ERROR
    assert response.message == "path: Is mandatory\npath: can't be blank"
