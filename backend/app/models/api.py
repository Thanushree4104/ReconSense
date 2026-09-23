from pydantic import BaseModel, ConfigDict


class ReconciliationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    payment_id: str
    status: str
    expected_amount: float
    settled_amount: float | None
    bank_amount: float | None
    difference: float
    exception_type: str | None


class InvestigationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    payment_id: str
    status: str
    exception_type: str

    expected_amount: float
    settled_amount: float | None
    bank_amount: float | None
    difference: float

    likely_cause: str
    confidence: float
    explanation: str
    recommendation: str
    governance_decision: str
    governance_reason: str
    evidence_references: list[str]

class EvidenceResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source: str
    reference: str
    description: str


class AuditEventResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    payment_id: str
    event_type: str
    actor: str
    description: str
    created_at: str