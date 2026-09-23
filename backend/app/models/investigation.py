from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class RecommendationType(StrEnum):
    REVIEW = "review"
    RETRY_RECONCILIATION = "retry_reconciliation"
    VERIFY_SETTLEMENT = "verify_settlement"
    VERIFY_BANK_ENTRY = "verify_bank_entry"
    ESCALATE = "escalate"


class InvestigationResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    payment_id: str
    exception_type: str
    likely_cause: str
    confidence: float = Field(ge=0, le=1)
    explanation: str
    recommendation: RecommendationType
    evidence_references: list[str] = Field(default_factory=list)