import pytest

from app.guardrails.investigation import InvestigationGuardrail
from app.models.investigation import (
    InvestigationResult,
    RecommendationType,
)
from app.models.reconciliation import Evidence


def make_investigation(
    confidence: float = 0.97,
    recommendation: RecommendationType = RecommendationType.VERIFY_BANK_ENTRY,
) -> InvestigationResult:
    return InvestigationResult(
        payment_id="PAY_004",
        exception_type="bank_mismatch",
        likely_cause="Bank credited an amount different from the expected settlement.",
        confidence=confidence,
        explanation="The settlement expects 2164.60, but the bank entry is 2100.00.",
        recommendation=recommendation,
        evidence_references=["SET_004", "BANK_004"],
    )


def make_evidence() -> list[Evidence]:
    return [
        Evidence(
            source="settlement",
            reference="SET_004",
            description="Expected bank credit: 2164.60.",
        ),
        Evidence(
            source="bank",
            reference="BANK_004",
            description="Actual bank amount: 2100.00.",
        ),
    ]


def test_valid_investigation_is_allowed() -> None:
    investigation = make_investigation()

    result = InvestigationGuardrail().validate(
        investigation,
        make_evidence(),
    )

    assert result == investigation


def test_invalid_evidence_reference_is_rejected() -> None:
    investigation = make_investigation()
    investigation.evidence_references = ["SET_004", "FAKE_EVIDENCE"]

    with pytest.raises(ValueError, match="FAKE_EVIDENCE"):
        InvestigationGuardrail().validate(
            investigation,
            make_evidence(),
        )


def test_low_confidence_investigation_is_rejected() -> None:
    investigation = make_investigation(confidence=0.65)

    with pytest.raises(ValueError, match="below the minimum threshold"):
        InvestigationGuardrail().validate(
            investigation,
            make_evidence(),
        )


def test_allowed_recommendation_is_accepted() -> None:
    investigation = make_investigation(
        recommendation=RecommendationType.VERIFY_BANK_ENTRY,
    )

    result = InvestigationGuardrail().validate(
        investigation,
        make_evidence(),
    )

    assert result.recommendation == RecommendationType.VERIFY_BANK_ENTRY