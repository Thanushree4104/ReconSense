from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class GovernanceDecision(StrEnum):
    ALLOWED = "allowed"
    APPROVAL_REQUIRED = "approval_required"
    BLOCKED = "blocked"


class GovernanceResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    payment_id: str
    recommendation: str
    decision: GovernanceDecision
    reason: str