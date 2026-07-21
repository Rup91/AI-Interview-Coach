"""Health check endpoint.

Used for liveness checks (load balancers, container orchestrators, local
verification). Not part of the interview API contract.
"""

from fastapi import APIRouter
from pydantic import BaseModel

from app.core.config import get_settings
from app.schemas.common import SuccessResponse

router = APIRouter(tags=["Health"])


class HealthData(BaseModel):
    status: str
    environment: str
    version: str


@router.get("/health", response_model=SuccessResponse[HealthData])
def health_check() -> SuccessResponse[HealthData]:
    settings = get_settings()
    return SuccessResponse(
        message="Service is healthy",
        data=HealthData(
            status="healthy",
            environment=settings.environment,
            version=settings.app_version,
        ),
    )
