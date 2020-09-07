"""Test prompt validation module."""
import git_portfolio.prompt_validation as pv


def test_ignore_if_not_confirmed_false() -> None:
    """Return true."""
    value = pv.ignore_if_not_confirmed({"confirmation": False})

    assert value is True


def test_ignore_if_not_confirmed_true() -> None:
    """Return false."""
    value = pv.ignore_if_not_confirmed({"confirmation": True})

    assert value is False


def test_not_empty_validation_all_spaces() -> None:
    """Return false."""
    value = pv.not_empty_validation({}, "   ")

    assert value is False


def test_not_empty_validation_some_spaces() -> None:
    """Return true."""
    value = pv.not_empty_validation({}, " x  ")

    assert value is True


def test_not_empty_validation_empty() -> None:
    """Return false."""
    value = pv.not_empty_validation({}, "")

    assert value is False
