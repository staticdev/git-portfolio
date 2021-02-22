"""Request for list of issues and/or pull requests."""
from collections.abc import Mapping
from typing import Dict
from typing import List
from typing import Optional
from typing import Union


class IssueListInvalidRequest:
    """Invalid request for list."""

    def __init__(self) -> None:
        """Initializer."""
        self.errors: List[Dict[str, str]] = []

    def add_error(self, parameter: str, message: str) -> None:
        """Add error to error list."""
        self.errors.append({"parameter": parameter, "message": message})

    def has_errors(self) -> bool:
        """Return if request has errors."""
        return len(self.errors) > 0

    def __bool__(self) -> bool:
        """Bool return for success."""
        return False


class IssueListValidRequest:
    """Valid request for list."""

    def __init__(self, filters: Optional[Dict[str, str]] = None) -> None:
        """Initializer."""
        self.filters = filters

    def __bool__(self) -> bool:
        """Bool return for success."""
        return True


def build_list_request(
    filters: Optional[Dict[str, str]] = None
) -> Union[IssueListInvalidRequest, IssueListValidRequest]:
    """Create request from filters."""
    accepted_filters = ["obj__eq", "state__eq", "title__contains"]
    invalid_req = IssueListInvalidRequest()

    if filters is not None:
        if not isinstance(filters, Mapping):
            invalid_req.add_error("filters", "Is not iterable")
            return invalid_req

        for key, value in filters.items():
            if key not in accepted_filters:
                invalid_req.add_error("filters", f"Key {key} cannot be used.")
            if (key == "obj__eq" and value not in ["pull request", "issue", "all"]) or (
                key == "state__eq" and value not in ["all", "open", "closed"]
            ):
                invalid_req.add_error(
                    "filters", f"Value {value} for key 'obj__eq' cannot be used."
                )
        if invalid_req.has_errors():
            return invalid_req

    return IssueListValidRequest(filters=filters)
