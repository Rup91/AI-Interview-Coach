"""Interview configuration, start, answer submission, and session-lookup endpoints.

Implements POST /interviews/configure, POST /interviews/{interview_id}/start,
POST /interviews/{interview_id}/answer/text, POST
/interviews/{interview_id}/answer/voice, and GET /interviews/{interview_id},
per API_CONTRACT.md sections 6(i)-(v). Complete Interview (a future
"Force Complete" feature) is intentionally not implemented yet.
"""

from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_interview_service
from app.business.exceptions import (
    InterviewAlreadyStartedError,
    InterviewNotFoundError,
    InterviewNotInProgressError,
    StaleAnswerSubmissionError,
)
from app.business.interview_service import InterviewService
from app.business.models import SubmitAnswerOutcome
from app.schemas.common import SuccessResponse
from app.schemas.interview import (
    AnswerEvaluationData,
    InterviewConfigureData,
    InterviewConfigureRequest,
    InterviewResultData,
    InterviewSessionData,
    NextQuestionData,
    StartInterviewData,
    SubmitTextAnswerRequest,
    SubmitVoiceAnswerData,
    SubmitVoiceAnswerRequest,
)

router = APIRouter(prefix="/interviews", tags=["Interviews"])


def _build_answer_evaluation_fields(outcome: SubmitAnswerOutcome) -> Dict[str, Any]:
    """Map a business-layer SubmitAnswerOutcome onto the shared response fields.

    Shared by both the text and voice routes so the "exactly one of
    nextQuestion/interviewResult" mapping lives in exactly one place.
    """
    next_question_data = None
    if outcome.next_question is not None:
        next_question_data = NextQuestionData(
            question_number=outcome.question_number,
            question=outcome.next_question,
        )

    interview_result_data = None
    if outcome.interview_result is not None:
        interview_result_data = InterviewResultData(
            overall_score=outcome.interview_result.overall_score,
            strengths=outcome.interview_result.strengths,
            improvement_areas=outcome.interview_result.improvement_areas,
            recommendation=outcome.interview_result.recommendation,
            summary=outcome.interview_result.summary,
        )

    return {
        "score": outcome.evaluation.score,
        "strengths": outcome.evaluation.strengths,
        "improvement_areas": outcome.evaluation.improvement_areas,
        "feedback": outcome.evaluation.feedback,
        "ideal_answer": outcome.evaluation.ideal_answer,
        "next_question": next_question_data,
        "interview_result": interview_result_data,
    }


@router.post(
    "/configure",
    response_model=SuccessResponse[InterviewConfigureData],
    status_code=status.HTTP_201_CREATED,
    summary="Configure a new interview session",
)
def configure_interview(
    payload: InterviewConfigureRequest,
    service: InterviewService = Depends(get_interview_service),
) -> SuccessResponse[InterviewConfigureData]:
    session = service.configure_interview(
        role=payload.role,
        job_description=payload.job_description,
        interaction_mode=payload.interaction_mode,
        experience_level=payload.experience_level,
    )
    return SuccessResponse(
        message="Interview configured successfully",
        data=InterviewConfigureData(
            interview_id=session.interview_id,
            status=session.status.value,
        ),
    )


@router.post(
    "/{interview_id}/start",
    response_model=SuccessResponse[StartInterviewData],
    status_code=status.HTTP_200_OK,
    summary="Start a configured interview session",
)
def start_interview(
    interview_id: str,
    service: InterviewService = Depends(get_interview_service),
) -> SuccessResponse[StartInterviewData]:
    try:
        session = service.start_interview(interview_id)
    except InterviewNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except InterviewAlreadyStartedError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    return SuccessResponse(
        message="Interview started successfully",
        data=StartInterviewData(
            question_number=session.questions_asked + 1,
            question=session.current_question,
        ),
    )


@router.post(
    "/{interview_id}/answer/text",
    response_model=SuccessResponse[AnswerEvaluationData],
    status_code=status.HTTP_200_OK,
    summary="Submit a text answer",
)
def submit_text_answer(
    interview_id: str,
    payload: SubmitTextAnswerRequest,
    service: InterviewService = Depends(get_interview_service),
) -> SuccessResponse[AnswerEvaluationData]:
    try:
        outcome = service.submit_answer(interview_id, answer_text=payload.answer)
    except InterviewNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except InterviewNotInProgressError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except StaleAnswerSubmissionError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    return SuccessResponse(
        message="Answer evaluated successfully",
        data=AnswerEvaluationData(**_build_answer_evaluation_fields(outcome)),
    )


@router.post(
    "/{interview_id}/answer/voice",
    response_model=SuccessResponse[SubmitVoiceAnswerData],
    status_code=status.HTTP_200_OK,
    summary="Submit a voice answer",
)
def submit_voice_answer(
    interview_id: str,
    payload: SubmitVoiceAnswerRequest,
    service: InterviewService = Depends(get_interview_service),
) -> SuccessResponse[SubmitVoiceAnswerData]:
    try:
        outcome = service.submit_answer(interview_id, audio_file=payload.audio_file)
    except InterviewNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except InterviewNotInProgressError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except StaleAnswerSubmissionError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    return SuccessResponse(
        message="Answer evaluated successfully",
        data=SubmitVoiceAnswerData(
            transcription=outcome.transcription,
            **_build_answer_evaluation_fields(outcome),
        ),
    )


@router.get(
    "/{interview_id}",
    response_model=SuccessResponse[InterviewSessionData],
    status_code=status.HTTP_200_OK,
    summary="Retrieve current interview session state",
)
def get_interview_session(
    interview_id: str,
    service: InterviewService = Depends(get_interview_service),
) -> SuccessResponse[InterviewSessionData]:
    try:
        session = service.get_session(interview_id)
    except InterviewNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    current_question_data = None
    if session.current_question is not None:
        current_question_data = NextQuestionData(
            question_number=session.questions_asked + 1,
            question=session.current_question,
        )

    return SuccessResponse(
        message="Interview session retrieved successfully",
        data=InterviewSessionData(
            interview_id=session.interview_id,
            status=session.status.value,
            interaction_mode=session.interaction_mode.value,
            current_question=current_question_data,
            questions_answered=session.questions_asked,
            average_score=service.average_score(session),
        ),
    )
