from fastapi import APIRouter, HTTPException

from app.db.database import SessionLocal
from app.db.repository import AuditEventRepository, EvidenceRepository
from app.models.api import (
    AuditEventResponse,
    EvidenceResponse,
    InvestigationResponse,
    ReconciliationResponse,
)
from app.services.audit import AuditService
from app.services.evidence import EvidenceService
from app.services.investigation_workflow import run_investigation_workflow
from app.services.reconciliation_runner import run_reconciliation

router = APIRouter()


# ============================================================
# HEALTH
# ============================================================

@router.get("/health")
def health_check() -> dict[str, str]:
    """Return API health status."""
    return {"status": "ok"}


# ============================================================
# RECONCILIATION
# ============================================================

@router.get(
    "/reconciliation",
    response_model=list[ReconciliationResponse],
)
def get_reconciliation() -> list[ReconciliationResponse]:
    """Run reconciliation and return the results."""
    results = run_reconciliation()

    return [
        ReconciliationResponse(
            payment_id=result.payment_id,
            status=result.status.value,
            expected_amount=result.expected_amount,
            settled_amount=result.settled_amount,
            bank_amount=result.bank_amount,
            difference=result.difference,
            exception_type=(
                result.exception_type.value
                if result.exception_type
                else None
            ),
        )
        for result in results
    ]


@router.get("/reconciliation/summary")
def get_reconciliation_summary() -> dict:
    """Return batch reconciliation metrics and exception distribution."""
    results = run_reconciliation()

    total = len(results)

    matched = sum(
        1
        for result in results
        if result.status.value == "matched"
    )

    exceptions = sum(
        1
        for result in results
        if result.status.value == "exception"
    )

    exception_distribution: dict[str, int] = {}

    for result in results:
        if result.exception_type:
            exception_type = result.exception_type.value

            exception_distribution[exception_type] = (
                exception_distribution.get(exception_type, 0) + 1
            )

    match_rate = (
        matched / total * 100
        if total
        else 0.0
    )

    return {
        "total_records": total,
        "matched": matched,
        "exceptions": exceptions,
        "match_rate": round(match_rate, 2),
        "exception_distribution": exception_distribution,
    }


# ============================================================
# INVESTIGATIONS
# ============================================================

@router.get(
    "/investigations",
    response_model=list[InvestigationResponse],
)
def get_investigations() -> list[InvestigationResponse]:
    """Run the investigation workflow and return investigation cases."""

    cases = run_investigation_workflow()

    return [
        InvestigationResponse(
            payment_id=case.reconciliation.payment_id,
            status=case.reconciliation.status.value,
            exception_type=case.investigation.exception_type,
            expected_amount=float(
                case.reconciliation.expected_amount
            ),
            settled_amount=(
                float(case.reconciliation.settled_amount)
                if case.reconciliation.settled_amount is not None
                else None
            ),
            bank_amount=(
                float(case.reconciliation.bank_amount)
                if case.reconciliation.bank_amount is not None
                else None
            ),
            difference=float(
                case.reconciliation.difference
            ),
            likely_cause=case.investigation.likely_cause,
            confidence=case.investigation.confidence,
            explanation=case.investigation.explanation,
            recommendation=(
                case.investigation.recommendation.value
            ),
            governance_decision=(
                case.governance.decision.value
            ),
            governance_reason=case.governance.reason,
            evidence_references=(
                case.investigation.evidence_references
            ),
        )
        for case in cases
    ]


@router.get("/investigations/summary")
def get_investigation_summary() -> dict:
    """Return batch AI investigation and governance metrics."""

    cases = run_investigation_workflow()

    total_exceptions = len(cases)

    autonomously_resolved = sum(
        1
        for case in cases
        if case.is_resolved
    )

    approval_required = sum(
        1
        for case in cases
        if case.governance.decision.value == "approval_required"
    )

    unresolved = total_exceptions - autonomously_resolved

    resolution_rate = (
        autonomously_resolved / total_exceptions * 100
        if total_exceptions
        else 0.0
    )

    unresolved_by_exception_type: dict[str, int] = {}

    unresolved_cases = []

    for case in cases:
        if not case.is_resolved:
            exception_type = case.investigation.exception_type

            unresolved_by_exception_type[exception_type] = (
                unresolved_by_exception_type.get(
                    exception_type,
                    0,
                )
                + 1
            )

            unresolved_cases.append(
                {
                    "payment_id": (
                        case.reconciliation.payment_id
                    ),
                    "exception_type": exception_type,
                    "likely_cause": (
                        case.investigation.likely_cause
                    ),
                    "confidence": (
                        case.investigation.confidence
                    ),
                    "recommendation": (
                        case.investigation.recommendation.value
                    ),
                    "governance_decision": (
                        case.governance.decision.value
                    ),
                    "governance_reason": (
                        case.governance.reason
                    ),
                }
            )

    return {
        "total_exceptions": total_exceptions,
        "autonomously_resolved": autonomously_resolved,
        "approval_required": approval_required,
        "unresolved": unresolved,
        "resolution_rate": round(resolution_rate, 2),
        "unresolved_by_exception_type": (
            unresolved_by_exception_type
        ),
        "unresolved_cases": unresolved_cases,
    }


# ============================================================
# SINGLE INVESTIGATION
# ============================================================

@router.get(
    "/investigations/{payment_id}",
    response_model=InvestigationResponse,
)
def get_investigation(
    payment_id: str,
) -> InvestigationResponse:
    """Return the investigation for one payment."""

    cases = run_investigation_workflow(payment_id)

    for case in cases:
        if case.reconciliation.payment_id == payment_id:
            return InvestigationResponse(
                payment_id=case.reconciliation.payment_id,
                status=case.reconciliation.status.value,
                exception_type=case.investigation.exception_type,
                expected_amount=float(
                    case.reconciliation.expected_amount
                ),
                settled_amount=(
                    float(
                        case.reconciliation.settled_amount
                    )
                    if case.reconciliation.settled_amount
                    is not None
                    else None
                ),
                bank_amount=(
                    float(
                        case.reconciliation.bank_amount
                    )
                    if case.reconciliation.bank_amount
                    is not None
                    else None
                ),
                difference=float(
                    case.reconciliation.difference
                ),
                likely_cause=case.investigation.likely_cause,
                confidence=case.investigation.confidence,
                explanation=case.investigation.explanation,
                recommendation=(
                    case.investigation.recommendation.value
                ),
                governance_decision=(
                    case.governance.decision.value
                ),
                governance_reason=case.governance.reason,
                evidence_references=(
                    case.investigation.evidence_references
                ),
            )

    raise HTTPException(
        status_code=404,
        detail=(
            f"Investigation not found for payment "
            f"{payment_id}."
        ),
    )


# ============================================================
# APPROVAL
# ============================================================

@router.post(
    "/investigations/{payment_id}/approve",
)
def approve_investigation_action(
    payment_id: str,
) -> dict[str, str]:
    """
    Record human approval of the recommended investigation action.
    """

    cases = run_investigation_workflow(payment_id)

    case = next(
        (
            item
            for item in cases
            if item.reconciliation.payment_id == payment_id
        ),
        None,
    )

    if case is None:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Investigation not found for payment "
                f"{payment_id}."
            ),
        )

    if case.governance.decision.value != "approval_required":
        raise HTTPException(
            status_code=400,
            detail=(
                "This investigation does not require "
                "human approval."
            ),
        )

    db = SessionLocal()

    try:
        service = AuditService(
            AuditEventRepository(db)
        )

        service.record(
            payment_id=payment_id,
            event_type="action_approved",
            actor="human_operator",
            description=(
                "Human approval recorded for recommended "
                "action: "
                f"{case.investigation.recommendation.value}."
            ),
        )

        return {
            "status": "approved",
            "payment_id": payment_id,
            "recommendation": (
                case.investigation.recommendation.value
            ),
            "message": (
                "Human approval recorded in the audit trail."
            ),
        }

    finally:
        db.close()


# ============================================================
# EVIDENCE
# ============================================================

@router.get(
    "/investigations/{payment_id}/evidence",
    response_model=list[EvidenceResponse],
)
def get_investigation_evidence(
    payment_id: str,
) -> list[EvidenceResponse]:
    """Return evidence collected for one payment."""

    db = SessionLocal()

    try:
        service = EvidenceService(
            EvidenceRepository(db)
        )

        evidence = service.get_for_payment(payment_id)

        if not evidence:
            raise HTTPException(
                status_code=404,
                detail=(
                    f"Evidence not found for payment "
                    f"{payment_id}."
                ),
            )

        return [
            EvidenceResponse(
                source=item.source,
                reference=item.reference,
                description=item.description,
            )
            for item in evidence
        ]

    finally:
        db.close()


# ============================================================
# AUDIT TRAIL
# ============================================================

@router.get(
    "/investigations/{payment_id}/audit",
    response_model=list[AuditEventResponse],
)
def get_investigation_audit(
    payment_id: str,
) -> list[AuditEventResponse]:
    """Return audit events for one payment."""

    db = SessionLocal()

    try:
        service = AuditService(
            AuditEventRepository(db)
        )

        events = service.get_for_payment(payment_id)

        if not events:
            raise HTTPException(
                status_code=404,
                detail=(
                    f"Audit events not found for payment "
                    f"{payment_id}."
                ),
            )

        return [
            AuditEventResponse(
                payment_id=event.payment_id,
                event_type=event.event_type,
                actor=event.actor,
                description=event.description,
                created_at=event.created_at.isoformat(),
            )
            for event in events
        ]

    finally:
        db.close()