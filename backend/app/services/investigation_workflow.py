from app.agents.investigation import (
    DeterministicInvestigationProvider,
    GroqInvestigationProvider,
    InvestigationAgent,
)
from app.db.database import SessionLocal
from app.db.repository import AuditEventRepository, EvidenceRepository
from app.governance.models import GovernanceResult
from app.governance.policy import PolicyEngine
from app.guardrails.investigation import InvestigationGuardrail
from app.models.investigation import InvestigationResult
from app.models.reconciliation import Evidence, ReconciliationResult
from app.services.audit import AuditService
from app.services.evidence import EvidenceService
from app.services.reconciliation_runner import run_reconciliation


class InvestigationCase:
    """Complete investigation result for one reconciliation exception."""

    def __init__(
        self,
        reconciliation: ReconciliationResult,
        investigation: InvestigationResult,
        governance: GovernanceResult,
        evidence: list[Evidence],
    ) -> None:
        self.reconciliation = reconciliation
        self.investigation = investigation
        self.governance = governance
        self.evidence = evidence

    @property
    def is_resolved(self) -> bool:
        """Return whether the exception can be safely resolved."""
        return (
            self.investigation.confidence >= 0.80
            and self.governance.decision.value == "allowed"
        )

def run_investigation_workflow(
    payment_id: str | None = None,
) -> list[InvestigationCase]:
    """Run reconciliation, investigation, governance, and audit.

    If payment_id is provided, only that payment is investigated.
    Otherwise, all payments are investigated.
    """
    reconciliation_results = run_reconciliation()

    if payment_id is not None:
        reconciliation_results = [
            result
            for result in reconciliation_results
            if result.payment_id == payment_id
        ]
    else:
    # Investigate only reconciliation exceptions.
    # Matched records do not require an investigation.
        reconciliation_results = [
            result
            for result in reconciliation_results
            if result.status.value == "exception"
        ]
    
    db = SessionLocal()

    try:
        evidence_service = EvidenceService(EvidenceRepository(db))
        audit_service = AuditService(AuditEventRepository(db))
        investigation_agent = InvestigationAgent(
            provider=GroqInvestigationProvider(),
            fallback_provider=DeterministicInvestigationProvider(),
        )
        policy_engine = PolicyEngine()
        guardrail = InvestigationGuardrail()

        cases: list[InvestigationCase] = []

        for result in reconciliation_results:
            evidence = evidence_service.get_for_payment(
                result.payment_id
            )

            investigation = investigation_agent.investigate(
                result=result,
                evidence=evidence,
            )

            investigation = guardrail.validate(
                investigation=investigation,
                evidence=evidence,
            )

            governance = policy_engine.evaluate(investigation)

            audit_service.record(
                payment_id=result.payment_id,
                event_type="investigation_completed",
                actor="system",
                description=(
                    f"Investigation completed: "
                    f"{investigation.exception_type}; "
                    f"recommendation={investigation.recommendation}; "
                    f"decision={governance.decision}."
                ),
            )

            cases.append(
                InvestigationCase(
                    reconciliation=result,
                    investigation=investigation,
                    governance=governance,
                    evidence=evidence,
                )
            )

        return cases

    finally:
        db.close()


if __name__ == "__main__":
    for case in run_investigation_workflow():
        print(
            case.reconciliation.payment_id,
            "->",
            case.investigation.likely_cause,
            "| confidence:",
            case.investigation.confidence,
            "| decision:",
            case.governance.decision,
        )