from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.core.enums import ExceptionType, ReconciliationStatus


class Evidence(BaseModel):
    """A piece of evidence supporting a reconciliation conclusion."""

    model_config = ConfigDict(extra="forbid")

    source: str
    reference: str
    description: str


class ReconciliationResult(BaseModel):
    """Deterministic result produced by the reconciliation engine."""

    model_config = ConfigDict(extra="forbid")

    payment_id: str
    status: ReconciliationStatus
    expected_amount: Decimal
    settled_amount: Decimal | None = None
    bank_amount: Decimal | None = None
    difference: Decimal = Field(default=Decimal(0))
    exception_type: ExceptionType | None = None
    evidence: list[Evidence] = Field(default_factory=list)