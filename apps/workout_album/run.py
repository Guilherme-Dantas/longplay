from __future__ import annotations

from pydantic import BaseModel, Field


class RunRequest(BaseModel):
    duration_minutes: float = Field(gt=0, le=240)
    criteria: str = Field(min_length=1)
    tolerance_minutes: float = Field(default=5.0, ge=0, le=60)


def user_message(req: RunRequest) -> str:
    return (
        f"Timed session: {req.duration_minutes} minutes "
        f"(tolerance ±{req.tolerance_minutes} minutes).\n"
        f"Listening criteria: {req.criteria}"
    )
