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


class InterviewNotInProgressError(Exception):
    """Raised when an answer is submitted to a session that isn't 'In Progress'.

    Covers submitting before Start Interview has been called (still
    'Configured') and submitting after the interview has already
    'Completed'.
    """

    def __init__(self, interview_id: str, current_status: SessionStatus) -> None:
        self.interview_id = interview_id
        self.current_status = current_status
        super().__init__(
            f"Cannot submit an answer for interview '{interview_id}' because its "
            f"status is '{current_status.value}', not 'In Progress'."
        )


class StaleAnswerSubmissionError(Exception):
    """Raised when a submitted answer no longer matches the session's current question.

    Distinct from InterviewNotInProgressError: the session IS 'In
    Progress', but this specific submission was evaluated against a
    question the interview has since moved past - e.g. a duplicate
    request racing a first submission for the same question. Maps to the
    same 409 as InterviewNotInProgressError at the API layer, but keeps
    the message accurate to what actually happened.
    """

    def __init__(self, interview_id: str) -> None:
        self.interview_id = interview_id
        super().__init__(
            f"Interview '{interview_id}' has already moved past the question this "
            "answer was evaluated against - this submission is stale (likely a "
            "duplicate or late retry) and was not recorded."
        )
