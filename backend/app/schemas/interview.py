"""Request/response schemas for the Configure and Start Interview APIs.

Shapes and constraints here must match API_CONTRACT.md section 6(i)/(ii)
exactly. Enums are reused from the Business Layer (app.business.models)
rather than redefined, since plain string enums carry no pydantic-specific
behavior - avoiding two vocabularies for the same domain concept.
"""

from typing import Optional

from pydantic import Field, field_validator

from app.business.models import ExperienceLevel, InteractionMode
from app.schemas.common import CamelCaseModel


class InterviewConfigureRequest(CamelCaseModel):
    """Request body for POST /interviews/configure."""

    role: str = Field(..., min_length=1)
    job_description: Optional[str] = None
    interaction_mode: InteractionMode
    experience_level: ExperienceLevel

    @field_validator("role")
    @classmethod
    def role_must_not_be_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("role must not be blank")
        return stripped

    @field_validator("job_description")
    @classmethod
    def normalize_job_description(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None


class InterviewConfigureData(CamelCaseModel):
    """Response payload for a successfully configured interview.

    "interviewID" (capital ID) is the exact casing used in
    API_CONTRACT.md's response example, which differs from this field's
    standard camelCase conversion ("interviewId") - so it is pinned
    explicitly rather than left to the alias generator.
    """

    interview_id: str = Field(alias="interviewID")
    status: str


class StartInterviewData(CamelCaseModel):
    """Response payload for a successfully started interview."""

    question_number: int
    question: str
