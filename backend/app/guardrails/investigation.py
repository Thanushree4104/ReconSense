from typing import ClassVar

from app.models.investigation import (
    InvestigationResult,
    RecommendationType,
)
from app.models.reconciliation import Evidence


class InvestigationGuardrail:
    """Validate investigation results before they are accepted."""

    MIN_CONFIDENCE = 0.80

    ALLOWED_RECOMMENDATIONS: ClassVar[set[RecommendationType]] = {
        RecommendationType.REVIEW,
        RecommendationType.RETRY_RECONCILIATION,
        RecommendationType.VERIFY_SETTLEMENT,
        RecommendationType.VERIFY_BANK_ENTRY,
        RecommendationType.ESCALATE,
    }

    def validate(
        self,
        investigation: InvestigationResult,
        evidence: list[Evidence],
    ) -> InvestigationResult:
        """Validate evidence, confidence, and recommended action."""

        # 1. Evidence grounding
        valid_references = {item.reference for item in evidence}

        invalid_references = [
            reference
            for reference in investigation.evidence_references
            if reference not in valid_references
        ]

        if invalid_references:
            raise ValueError(
                "Investigation references unavailable evidence: "
                + ", ".join(invalid_references)
            )

        # 2. Confidence threshold
        if investigation.confidence < self.MIN_CONFIDENCE:
            raise ValueError(
                f"Investigation confidence {investigation.confidence:.2f} "
                f"is below the minimum threshold "
                f"{self.MIN_CONFIDENCE:.2f}."
            )

        # 3. Action allowlist
        if investigation.recommendation not in self.ALLOWED_RECOMMENDATIONS:
            raise ValueError(
                "Investigation contains an unsupported recommendation: "
                f"{investigation.recommendation}"
            )

        return investigation