from app.governance.models import GovernanceDecision, GovernanceResult
from app.models.investigation import InvestigationResult, RecommendationType


class PolicyEngine:
    """Apply governance rules to investigation recommendations."""

    def evaluate(
        self,
        investigation: InvestigationResult,
    ) -> GovernanceResult:
        recommendation = investigation.recommendation
        exception_type = investigation.exception_type

        # High-risk financial exceptions must always receive human review.
        # The AI recommendation cannot override this policy.
        approval_required_exceptions = {
            "duplicate_settlement",
        }

        if exception_type in approval_required_exceptions:
            return GovernanceResult(
                payment_id=investigation.payment_id,
                recommendation=recommendation,
                decision=GovernanceDecision.APPROVAL_REQUIRED,
                reason=(
                    f"The {exception_type} exception involves a high-risk "
                    "financial discrepancy and requires human review."
                ),
            )

        if recommendation in {
            RecommendationType.RETRY_RECONCILIATION,
            RecommendationType.VERIFY_SETTLEMENT,
        }:
            return GovernanceResult(
                payment_id=investigation.payment_id,
                recommendation=recommendation,
                decision=GovernanceDecision.ALLOWED,
                reason="The recommended action is a low-risk investigation step.",
            )

        if recommendation in {
            RecommendationType.VERIFY_BANK_ENTRY,
            RecommendationType.REVIEW,
            RecommendationType.ESCALATE,
        }:
            return GovernanceResult(
                payment_id=investigation.payment_id,
                recommendation=recommendation,
                decision=GovernanceDecision.APPROVAL_REQUIRED,
                reason=(
                    "The recommended action requires human review "
                    "before proceeding."
                ),
            )

        return GovernanceResult(
            payment_id=investigation.payment_id,
            recommendation=recommendation,
            decision=GovernanceDecision.BLOCKED,
            reason="The requested action is not permitted by policy.",
        )