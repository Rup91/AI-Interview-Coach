"""In-memory storage for interview sessions.

Temporary stand-in for persistent storage (no database yet, per this
step's scope). Kept behind a small, storage-agnostic interface so a
future database-backed implementation can replace it without changing
the Business Layer or API Layer that depend on it.
"""

import threading
from typing import Optional

from app.business.exceptions import (
    InterviewAlreadyStartedError,
    InterviewNotFoundError,
    InterviewNotInProgressError,
    StaleAnswerSubmissionError,
)
from app.business.models import EvaluationResult, InterviewSession, SessionStatus


class InMemorySessionStore:
    """Thread-safe, process-local store of interview sessions keyed by ID."""

    def __init__(self) -> None:
        self._sessions: dict[str, InterviewSession] = {}
        self._lock = threading.Lock()

    def save(self, session: InterviewSession) -> None:
        """Persist (create or overwrite) a session."""
        with self._lock:
            self._sessions[session.interview_id] = session

    def get(self, interview_id: str) -> Optional[InterviewSession]:
        """Return the session for the given ID, or None if it doesn't exist."""
        with self._lock:
            return self._sessions.get(interview_id)

    def exists(self, interview_id: str) -> bool:
        """Return whether a session with the given ID has been stored."""
        with self._lock:
            return interview_id in self._sessions

    def transition_status(
        self,
        interview_id: str,
        *,
        expected_status: SessionStatus,
        new_status: SessionStatus,
    ) -> InterviewSession:
        """Atomically verify a session's current status and update it.

        Guards against two concurrent requests for the same interview (a
        double-click, a client retry) both passing a "status is X" check
        before either writes the new status: only the caller that observes
        `expected_status` under this single lock acquisition wins the
        transition; the other raises InterviewAlreadyStartedError.
        """
        with self._lock:
            session = self._sessions.get(interview_id)
            if session is None:
                raise InterviewNotFoundError(interview_id)
            if session.status != expected_status:
                raise InterviewAlreadyStartedError(interview_id, session.status)
            session.status = new_status
            return session

    def record_evaluated_answer(
        self,
        interview_id: str,
        *,
        expected_question: str,
        evaluation: EvaluationResult,
        is_complete: bool,
        next_question: Optional[str],
    ) -> InterviewSession:
        """Atomically commit one evaluated answer to a session.

        Verifies the session is still 'In Progress' and still expecting an
        answer to `expected_question` before committing - this closes the
        same class of race transition_status() guards against, and also
        rejects a late/duplicate submission that was evaluated against a
        question the session has since moved past (rather than silently
        double-counting it). The two failure modes raise different
        exceptions so the error message stays accurate to what actually
        happened.
        """
        with self._lock:
            session = self._sessions.get(interview_id)
            if session is None:
                raise InterviewNotFoundError(interview_id)
            if session.status != SessionStatus.IN_PROGRESS:
                raise InterviewNotInProgressError(interview_id, session.status)
            if session.current_question != expected_question:
                raise StaleAnswerSubmissionError(interview_id)
            session.evaluation_history.append(evaluation)
            session.questions_asked += 1
            session.status = SessionStatus.COMPLETED if is_complete else SessionStatus.IN_PROGRESS
            session.current_question = None if is_complete else next_question
            return session
