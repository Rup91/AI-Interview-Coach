"""Business Layer: interview lifecycle operations.

Only Configure and Start Interview are implemented here. Get/Answer/
Complete are intentionally absent until those steps are approved.

This module has no dependency on FastAPI or Pydantic, so it can be
exercised independently of the API layer.
"""

import logging
from typing import Optional

from app.business.id_generator import SequentialIdGenerator
from app.business.models import ExperienceLevel, InteractionMode, InterviewSession, SessionStatus
from app.business.session_store import InMemorySessionStore
from app.knowledge.question_repository import QuestionRepository

logger = logging.getLogger(__name__)


class InterviewService:
    """Coordinates interview session creation and lifecycle transitions."""

    def __init__(
        self,
        session_store: InMemorySessionStore,
        id_generator: SequentialIdGenerator,
        question_repository: QuestionRepository,
        min_questions: int,
        max_questions: int,
    ) -> None:
        self._session_store = session_store
        self._id_generator = id_generator
        self._question_repository = question_repository
        self._min_questions = min_questions
        self._max_questions = max_questions

    def configure_interview(
        self,
        *,
        role: str,
        interaction_mode: InteractionMode,
        experience_level: ExperienceLevel,
        job_description: Optional[str] = None,
    ) -> InterviewSession:
        """Create and persist a new interview session in the 'Configured' state.

        The number of questions is not a client input: every session is
        created with the backend-controlled min/max bounds, and starts
        with zero questions asked.
        """
        interview_id = self._id_generator.generate()
        session = InterviewSession(
            interview_id=interview_id,
            role=role,
            job_description=job_description,
            interaction_mode=interaction_mode,
            experience_level=experience_level,
            min_questions=self._min_questions,
            max_questions=self._max_questions,
        )
        self._session_store.save(session)
        logger.info(
            "Interview configured: interview_id=%s role=%s interaction_mode=%s "
            "experience_level=%s min_questions=%s max_questions=%s",
            session.interview_id,
            session.role,
            session.interaction_mode.value,
            session.experience_level.value,
            session.min_questions,
            session.max_questions,
        )
        return session

    def start_interview(self, interview_id: str) -> InterviewSession:
        """Start a configured interview: move it to 'In Progress' and generate
        its first question.

        Raises InterviewNotFoundError if the session doesn't exist, or
        InterviewAlreadyStartedError if it isn't currently 'Configured'
        (the API layer maps these to 404/409 respectively).
        """
        session = self._session_store.transition_status(
            interview_id,
            expected_status=SessionStatus.CONFIGURED,
            new_status=SessionStatus.IN_PROGRESS,
        )
        question = self._question_repository.get_first_question(
            role=session.role,
            experience_level=session.experience_level,
        )
        session.current_question = question
        self._session_store.save(session)
        logger.info(
            "Interview started: interview_id=%s role=%s experience_level=%s",
            session.interview_id,
            session.role,
            session.experience_level.value,
        )
        return session
