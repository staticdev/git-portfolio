"""Response objects."""
from __future__ import annotations

from typing import Any
from typing import Dict
from typing import Optional
from typing import Union


class ResponseFailure:
    """Response failure class."""

    RESOURCE_ERROR = "ResourceError"
    PARAMETERS_ERROR = "ParametersError"
    SYSTEM_ERROR = "SystemError"

    def __init__(self, type_: str, message: Union[str, Exception, None]) -> None:
        """Constructor."""
        self.type = type_
        self.message = self._format_message(message)

    def _format_message(self, msg: Union[str, Exception, None]) -> Optional[str]:
        """Format message when it is an exception.

        Args:
            msg: string, exception or None.

        Returns:
            Union[str, None]: formatted message or None.
        """
        if isinstance(msg, Exception):
            return f"{msg.__class__.__name__}: {msg}"
        return msg

    @property
    def value(self) -> Dict[str, Optional[str]]:
        """Value property.

        Returns:
            Dict[str, str]: type and message.
        """
        return {"type": self.type, "message": self.message}

    def __bool__(self) -> bool:
        """Bool return for success."""
        return False

    @classmethod
    def build_resource_error(
        cls, message: Union[str, Exception, None] = None
    ) -> ResponseFailure:
        """Build a ResponseFailure with type resource error."""
        return cls(cls.RESOURCE_ERROR, message)

    @classmethod
    def build_system_error(
        cls, message: Union[str, Exception, None] = None
    ) -> ResponseFailure:
        """Build a ResponseFailure with type system error."""
        return cls(cls.SYSTEM_ERROR, message)

    @classmethod
    def build_parameters_error(
        cls, message: Union[str, Exception, None] = None
    ) -> ResponseFailure:
        """Build a ResponseFailure with type parameters error."""
        return cls(cls.PARAMETERS_ERROR, message)


class ResponseSuccess:
    """Response success class."""

    SUCCESS = "Success"

    def __init__(self, value: Any = None) -> None:
        """Constructor."""
        self.type = self.SUCCESS
        self.value = value

    def __bool__(self) -> bool:
        """Bool return for success."""
        return True
