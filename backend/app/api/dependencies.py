"""FastAPI dependency providers.

Centralizes construction of business-layer singletons so routers depend
on them via `Depends` rather than importing concrete classes directly -
swapping InMemorySessionStore for a database-backed store later touches
only this file. Mirrors the pattern already used by
app.core.config.get_settings.
"""

from functools import lru_cache

from app.business.id_generator import SequentialIdGenerator
from app.business.interview_service import InterviewService
from app.business.session_store import InMemorySessionStore
from app.core.config import get_settings
from app.knowledge.question_repository import QuestionRepository


@lru_cache
def get_session_store() -> InMemorySessionStore:
    return InMemorySessionStore()


@lru_cache
def get_id_generator() -> SequentialIdGenerator:
    return SequentialIdGenerator()


@lru_cache
def get_question_repository() -> QuestionRepository:
    return QuestionRepository()


@lru_cache
def get_interview_service() -> InterviewService:
    settings = get_settings()
    return InterviewService(
        session_store=get_session_store(),
        id_generator=get_id_generator(),
        question_repository=get_question_repository(),
        min_questions=settings.min_interview_questions,
        max_questions=settings.max_interview_questions,
    )
