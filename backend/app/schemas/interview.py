"""Request/response schemas for the Configure, Start, Submit Answer, and
Get Session APIs.

Shapes and constraints here must match API_CONTRACT.md section 6(i)-(v)
exactly. Enums are reused from the Business Layer (app.business.models)
rather than redefined, since plain string enums carry no pydantic-specific
behavior - avoiding two vocabularies for the same domain concept.
"""

from typing import List, Optional

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


class SubmitTextAnswerRequest(CamelCaseModel):
    """Request body for POST /interviews/{interview_id}/answer/text."""

    answer: str

    @field_validator("answer")
    @classmethod
    def normalize_answer(cls, value: str) -> str:
        # Deliberately not rejected when empty after stripping: a blank
        # answer is a legitimate "candidate could not answer" signal that
        # the (dummy, later AI-backed) evaluator should score, not a
        # validation failure.
        return value.strip()


class SubmitVoiceAnswerRequest(CamelCaseModel):
    """Request body for POST /interviews/{interview_id}/answer/voice.

    `audio_file` is an opaque reference string (e.g. a filename) per
    API_CONTRACT.md's literal example - not a real file upload.
    """

    audio_file: str = Field(..., min_length=1)

    @field_validator("audio_file")
    @classmethod
    def audio_file_must_not_be_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("audioFile must not be blank")
        return stripped


class NextQuestionData(CamelCaseModel):
    """The next interview question, embedded in a Submit Answer response."""

    question_number: int
    question: str


class InterviewResultData(CamelCaseModel):
    """The final, aggregated interview result, embedded in a Submit Answer response."""

    overall_score: int
    strengths: List[str]
    improvement_areas: List[str]
    recommendation: str
    summary: str


class AnswerEvaluationData(CamelCaseModel):
    """Response payload shared by both Submit Answer endpoints.

    Exactly one of `next_question`/`interview_result` is populated: the
    interview either continues (next_question) or has just completed
    (interview_result) - never both, never neither.
    """

    score: int
    strengths: List[str]
    improvement_areas: List[str]
    feedback: str
    ideal_answer: str
    next_question: Optional[NextQuestionData] = None
    interview_result: Optional[InterviewResultData] = None


class SubmitVoiceAnswerData(AnswerEvaluationData):
    """Response payload for Submit Voice Answer - adds the transcription."""

    transcription: str


class InterviewSessionData(CamelCaseModel):
    """Response payload for GET /interviews/{interview_id}.

    Deliberately excludes any question-count/total/percentage field -
    interview length is an adaptive, backend-only decision (see section
    6(i)). `current_question` is null when the interview hasn't started
    ('Configured') or has finished ('Completed'). `average_score` is
    null until at least one answer has been evaluated.
    """

    interview_id: str = Field(alias="interviewID")
    status: str
    interaction_mode: str
    current_question: Optional[NextQuestionData] = None
    questions_answered: int
    average_score: Optional[float] = None
