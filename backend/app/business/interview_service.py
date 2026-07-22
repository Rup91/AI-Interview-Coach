"""Business Layer: interview lifecycle operations.

Configure, Start, Submit Answer, and Get Session are implemented here.
Complete Interview (a future "Force Complete" feature) is intentionally
absent until it is approved - the interview otherwise completes on its
own through the Submit Answer flow.

This module has no dependency on FastAPI or Pydantic, so it can be
exercised independently of the API layer.
"""

import logging
from typing import Iterable, List, Optional

from app.business.evaluation_service import EvaluationService
from app.business.exceptions import InterviewNotFoundError, InterviewNotInProgressError
from app.business.id_generator import SequentialIdGenerator
from app.business.models import (
    ExperienceLevel,
    InteractionMode,
    InterviewResult,
    InterviewSession,
    SessionStatus,
    SubmitAnswerOutcome,
)
from app.business.session_store import InMemorySessionStore
from app.business.voice_service import VoiceService
from app.knowledge.question_generation_service import QuestionGenerationService
from app.knowledge.question_repository import QuestionRepository

logger = logging.getLogger(__name__)


class InterviewService:
    """Coordinates interview session creation and lifecycle transitions."""

    def __init__(
        self,
        session_store: InMemorySessionStore,
        id_generator: SequentialIdGenerator,
        question_repository: QuestionRepository,
        question_generation_service: QuestionGenerationService,
        evaluation_service: EvaluationService,
        voice_service: VoiceService,
        min_questions: int,
        max_questions: int,
        early_termination_score_threshold: float,
    ) -> None:
        self._session_store = session_store
        self._id_generator = id_generator
        self._question_repository = question_repository
        self._question_generation_service = question_generation_service
        self._evaluation_service = evaluation_service
        self._voice_service = voice_service
        self._min_questions = min_questions
        self._max_questions = max_questions
        self._early_termination_score_threshold = early_termination_score_threshold

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

    def get_session(self, interview_id: str) -> InterviewSession:
        """Retrieve an interview session as-is, with no state change.

        Raises InterviewNotFoundError if the session doesn't exist (the
        API layer maps this to 404).
        """
        session = self._session_store.get(interview_id)
        if session is None:
            raise InterviewNotFoundError(interview_id)
        return session

    def submit_answer(
        self,
        interview_id: str,
        *,
        answer_text: Optional[str] = None,
        audio_file: Optional[str] = None,
    ) -> SubmitAnswerOutcome:
        """Evaluate one submitted answer and advance the interview.

        Exactly one of `answer_text`/`audio_file` is expected (enforced by
        the two separate API routes, not here). Raises
        InterviewNotFoundError or InterviewNotInProgressError, mapped by
        the API layer to 404/409 respectively.

        Evaluation and question generation deliberately run without
        holding the session store's lock - they stand in for what will
        become real (and potentially slow) AI Gateway calls, and locking
        across those would serialize every session's traffic behind one
        lock. Only the final state commit (append + increment + advance)
        is atomic, via session_store.record_evaluated_answer.
        """
        session = self._session_store.get(interview_id)
        if session is None:
            raise InterviewNotFoundError(interview_id)
        if session.status != SessionStatus.IN_PROGRESS:
            raise InterviewNotInProgressError(interview_id, session.status)
        if session.current_question is None:
            # Structurally unreachable while status is IN_PROGRESS (Start Interview
            # and this method both always set current_question when leaving a
            # non-terminal state) - guarded defensively rather than assumed.
            raise RuntimeError(
                f"Interview '{interview_id}' is 'In Progress' but has no current "
                "question - internal inconsistency."
            )

        question_being_answered = session.current_question

        transcription: Optional[str] = None
        if audio_file is not None:
            transcription = self._voice_service.transcribe(audio_file)
            effective_answer = transcription
        else:
            effective_answer = answer_text or ""

        evaluation = self._evaluation_service.evaluate(
            question=question_being_answered,
            answer=effective_answer,
        )

        prospective_questions_asked = session.questions_asked + 1
        prospective_scores = [e.score for e in session.evaluation_history] + [evaluation.score]
        is_complete = self._should_complete(prospective_questions_asked, prospective_scores)

        next_question_text: Optional[str] = None
        if not is_complete:
            next_question_text = self._question_generation_service.generate_next_question(
                role=session.role,
                experience_level=session.experience_level,
                question_number=prospective_questions_asked + 1,
            )

        updated_session = self._session_store.record_evaluated_answer(
            interview_id,
            expected_question=question_being_answered,
            evaluation=evaluation,
            is_complete=is_complete,
            next_question=next_question_text,
        )

        interview_result = self._build_interview_result(updated_session) if is_complete else None

        logger.info(
            "Answer submitted: interview_id=%s questions_asked=%s score=%s completed=%s",
            interview_id,
            updated_session.questions_asked,
            evaluation.score,
            is_complete,
        )

        return SubmitAnswerOutcome(
            evaluation=evaluation,
            transcription=transcription,
            completed=is_complete,
            question_number=None if is_complete else prospective_questions_asked + 1,
            next_question=next_question_text,
            interview_result=interview_result,
        )

    def _should_complete(self, questions_asked: int, scores: List[int]) -> bool:
        """Decide continue-vs-complete per the approved business rule.

        - Below min_questions: never complete.
        - At exactly min_questions: complete only if the running average
          score is below the early-termination threshold - a single,
          one-time checkpoint, not a re-check on every later question.
        - Between min_questions and max_questions (past the checkpoint):
          always continue.
        - At or beyond max_questions: always complete.
        """
        if questions_asked < self._min_questions:
            return False
        if questions_asked >= self._max_questions:
            return True
        if questions_asked == self._min_questions:
            average = self._average_score(scores)
            return average is not None and average < self._early_termination_score_threshold
        return False

    def average_score(self, session: InterviewSession) -> Optional[float]:
        """Return the running average score across `session`'s evaluated answers.

        Public (unlike _average_score/_should_complete/_build_interview_result)
        because the API layer needs this for Get Session's response - it
        should compute it via the service, not by reaching into a private
        method or reimplementing the average itself.
        """
        return self._average_score([e.score for e in session.evaluation_history])

    def _build_interview_result(self, session: InterviewSession) -> InterviewResult:
        """Aggregate the full evaluation history into a final dummy report."""
        average = self.average_score(session) or 0.0
        overall_score = round(average * 10)  # 0-10 average -> 0-100 overall score

        strengths = self._aggregate_unique(e.strengths for e in session.evaluation_history)
        improvement_areas = self._aggregate_unique(
            e.improvement_areas for e in session.evaluation_history
        )

        if average < 4.0:
            recommendation = "Not recommended to proceed"
        elif average < 7.0:
            recommendation = "Recommended for further evaluation"
        elif average < 8.5:
            recommendation = "Recommended for next round"
        else:
            recommendation = "Strongly recommended for next round"

        summary = (
            f"The candidate completed {session.questions_asked} questions with an "
            f"overall score of {overall_score}%. Recommendation: {recommendation}."
        )

        return InterviewResult(
            overall_score=overall_score,
            strengths=strengths,
            improvement_areas=improvement_areas,
            recommendation=recommendation,
            summary=summary,
        )

    @staticmethod
    def _aggregate_unique(lists: Iterable[List[str]], limit: int = 5) -> List[str]:
        """Deduplicate items across several lists, preserving order, capped at `limit`."""
        seen: List[str] = []
        for items in lists:
            for item in items:
                if item not in seen:
                    seen.append(item)
        return seen[:limit]

    @staticmethod
    def _average_score(scores: List[int]) -> Optional[float]:
        """Return the average of `scores`, or None if the list is empty.

        Low-level helper operating on a plain score list (used by
        _should_complete with a *prospective* list that doesn't
        correspond to any saved session). average_score() wraps this for
        callers that have an actual InterviewSession.
        """
        if not scores:
            return None
        return sum(scores) / len(scores)
