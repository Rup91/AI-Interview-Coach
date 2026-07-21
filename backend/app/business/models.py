"""Domain-level models for interview sessions.

Framework-agnostic: no FastAPI or Pydantic imports. This lets the
Business Layer be reasoned about (and later tested) independently of the
API layer, per CLAUDE.md's "keep components loosely coupled" guideline.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


class SessionStatus(str, Enum):
    """Interview session lifecycle states, per CLAUDE.md's Session Management.

    Configured -> In Progress -> Completed.
    """

    CONFIGURED = "Configured"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"


class InteractionMode(str, Enum):
    """How the candidate interacts with the interview."""

    TEXT = "text"
    VOICE = "voice"
    TEXT_VOICE = "text_voice"


class ExperienceLevel(str, Enum):
    """Industry-standard experience bands.

    Bands (by years of experience) used to derive these labels:
        0-3 years   -> Junior
        3-8 years   -> Mid-Level
        8-12 years  -> Senior
        12-16 years -> Lead
        16-20 years -> Principal
        20-25+ years -> Distinguished
    """

    JUNIOR = "Junior"
    MID_LEVEL = "Mid-Level"
    SENIOR = "Senior"
    LEAD = "Lead"
    PRINCIPAL = "Principal"
    DISTINGUISHED = "Distinguished"


@dataclass
class InterviewSession:
    """An interview session held in memory for the lifetime of the process.

    The final number of questions asked is a backend-controlled decision,
    not a client input: every interview asks at least `min_questions`, and
    may continue up to `max_questions` depending on candidate performance
    (evaluated question-by-question during the Answer flow, not here).
    """

    interview_id: str
    role: str
    interaction_mode: InteractionMode
    experience_level: ExperienceLevel
    min_questions: int
    max_questions: int
    job_description: Optional[str] = None
    status: SessionStatus = SessionStatus.CONFIGURED
    questions_asked: int = 0
    current_question: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
