"""Common response envelopes shared by every API endpoint.

These mirror the structures defined in API_CONTRACT.md sections 4 and 5.
All endpoints must respond using one of these two shapes so that frontend
consumers can rely on a single, consistent contract.
"""

from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

DataT = TypeVar("DataT")


class CamelCaseModel(BaseModel):
    """Base for API schemas that exchange camelCase JSON.

    Python attributes stay snake_case (idiomatic) while requests are
    parsed from, and responses are serialized to, camelCase - matching
    API_CONTRACT.md's field naming (e.g. "jobDescription").
    """

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )


class SuccessResponse(BaseModel, Generic[DataT]):
    success: bool = True
    message: str
    data: DataT


class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    errors: list[str] = []
