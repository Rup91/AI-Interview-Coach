"""Interview configuration and start endpoints.

Implements POST /interviews/configure and POST /interviews/{interview_id}/start,
per API_CONTRACT.md sections 6(i) and 6(ii). Other interview endpoints
(get, answer, complete) are intentionally not implemented yet.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_interview_service
from app.business.exceptions import InterviewAlreadyStartedError, InterviewNotFoundError
from app.business.interview_service import InterviewService
from app.schemas.common import SuccessResponse
from app.schemas.interview import (
    InterviewConfigureData,
    InterviewConfigureRequest,
    StartInterviewData,
)

router = APIRouter(prefix="/interviews", tags=["Interviews"])


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
