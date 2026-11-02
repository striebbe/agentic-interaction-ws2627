"""Custom types for the calendar assistant."""

from enum import Enum


class Event(Enum):
    """Event types written to the run log (field ``event``)."""

    USER_TASK = "user_task"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    FINAL = "final"
    ERROR = "error"
