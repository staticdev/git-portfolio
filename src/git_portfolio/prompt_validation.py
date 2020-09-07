"""Prompt validation module."""
from typing import Any
from typing import Dict


def ignore_if_not_confirmed(answers: Dict[str, Any]) -> bool:
    """Ignore if not confirmed question."""
    return not answers["confirmation"]


def not_empty_validation(answers: Dict[str, Any], current: str) -> bool:
    """Validade if current answer is not just spaces.

    Args:
        answers (Dict[str, Any]): answers to previous questions (ignored).
        current (str): answer to current question.

    Returns:
        bool: if is valid output.
    """
    current_without_spaces = current.strip()
    return True if current_without_spaces else False
