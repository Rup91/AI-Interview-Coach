"""Domain exceptions for the interview business layer.

Plain exceptions with no FastAPI/HTTP knowledge - the API layer is
responsible for translating these into HTTP status codes, keeping the
Business Layer unaware of transport concerns.
"""

from app.business.models import SessionStatus


class InterviewNotFoundError(Exception):
    """Raised when no interview session exists for the given ID."""

    def __init__(self, interview_id: str) -> None:
        self.interview_id = interview_id
        super().__init__(f"Interview '{interview_id}' was not found.")


class InterviewAlreadyStartedError(Exception):
    """Raised when Start Interview is called on a session that is not 'Configured'.

    Covers every non-Configured state (already In Progress, already
    Completed) - any of these means the interview cannot be started again.
    """

    def __init__(self, interview_id: str, current_status: SessionStatus) -> None:
        self.interview_id = interview_id
        self.current_status = current_status
        super().__init__(
            f"Interview '{interview_id}' cannot be started because its status is "
            f"'{current_status.value}'."
        )
