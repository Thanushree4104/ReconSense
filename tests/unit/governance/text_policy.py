from app.governance.models import GovernanceDecision
from app.governance.policy import PolicyEngine
from app.models.investigation import (
    InvestigationResult,
    RecommendationType,
)


def make_investigation(
    recommendation: RecommendationType,
) -> InvestigationResult:
    return InvestigationResult(
        payment_id="PAY_TEST",
        exception_type="test_exception",
        likely_cause="Test cause",
        confidence=0.95,
        explanation="Test explanation",
        recommendation=recommendation,
        evidence_references=["TEST_001"],
    )


def test_retry_reconciliation_is_allowed() -> None:
    engine = PolicyEngine()

    result = engine.evaluate(
        make_investigation(RecommendationType.RETRY_RECONCILIATION)
    )

    assert result.decision == GovernanceDecision.ALLOWED


def test_verify_settlement_is_allowed() -> None:
    engine = PolicyEngine()

    result = engine.evaluate(
        make_investigation(RecommendationType.VERIFY_SETTLEMENT)
    )

    assert result.decision == GovernanceDecision.ALLOWED


def test_verify_bank_entry_requires_approval() -> None:
    engine = PolicyEngine()

    result = engine.evaluate(
        make_investigation(RecommendationType.VERIFY_BANK_ENTRY)
    )

    assert result.decision == GovernanceDecision.APPROVAL_REQUIRED


def test_review_requires_approval() -> None:
    engine = PolicyEngine()

    result = engine.evaluate(
        make_investigation(RecommendationType.REVIEW)
    )

    assert result.decision == GovernanceDecision.APPROVAL_REQUIRED


def test_escalate_requires_approval() -> None:
    engine = PolicyEngine()

    result = engine.evaluate(
        make_investigation(RecommendationType.ESCALATE)
    )

    assert result.decision == GovernanceDecision.APPROVAL_REQUIRED