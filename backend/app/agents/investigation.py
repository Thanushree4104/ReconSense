import json
from abc import ABC, abstractmethod

from groq import Groq

from app.core.config import settings
from app.models.investigation import (
    InvestigationResult,
    RecommendationType,
)
from app.models.reconciliation import Evidence, ReconciliationResult


class InvestigationProvider(ABC):
    """Interface for investigation providers."""

    @abstractmethod
    def investigate(
        self,
        result: ReconciliationResult,
        evidence: list[Evidence],
    ) -> InvestigationResult:
        """Investigate a reconciliation exception."""


class DeterministicInvestigationProvider(InvestigationProvider):
    """Rule-based investigation provider used as a reliable fallback."""

    def investigate(
        self,
        result: ReconciliationResult,
        evidence: list[Evidence],
    ) -> InvestigationResult:

        evidence_references = [
            item.reference for item in evidence
        ]

        if result.exception_type is None:
            return InvestigationResult(
                payment_id=result.payment_id,
                exception_type="none",
                likely_cause="No reconciliation exception detected.",
                confidence=1.0,
                explanation=(
                    "The payment matched the available settlement "
                    "and bank records."
                ),
                recommendation=RecommendationType.RETRY_RECONCILIATION,
                evidence_references=evidence_references,
            )

        exception_type = result.exception_type

        if exception_type == "amount_mismatch":
            return InvestigationResult(
                payment_id=result.payment_id,
                exception_type=exception_type,
                likely_cause=(
                    "Payment amount differs from the settlement "
                    "gross amount."
                ),
                confidence=0.98,
                explanation=(
                    f"The expected payment amount is "
                    f"{result.expected_amount}, while the settled "
                    f"amount is {result.settled_amount}. This indicates "
                    "that the settlement does not fully correspond "
                    "to the payment."
                ),
                recommendation=RecommendationType.VERIFY_SETTLEMENT,
                evidence_references=evidence_references,
            )

        if exception_type == "missing_settlement":
            return InvestigationResult(
                payment_id=result.payment_id,
                exception_type=exception_type,
                likely_cause=(
                    "No valid settled settlement record was found."
                ),
                confidence=0.99,
                explanation=(
                    "The payment exists, but a corresponding settled "
                    "settlement record could not be found."
                ),
                recommendation=RecommendationType.VERIFY_SETTLEMENT,
                evidence_references=evidence_references,
            )

        if exception_type == "bank_mismatch":
            return InvestigationResult(
                payment_id=result.payment_id,
                exception_type=exception_type,
                likely_cause=(
                    "Bank transaction amount differs from the "
                    "expected settlement amount."
                ),
                confidence=0.97,
                explanation=(
                    f"The expected bank amount is based on the "
                    f"settlement amount of {result.settled_amount}, "
                    f"but the recorded bank amount is "
                    f"{result.bank_amount}. This suggests a "
                    "discrepancy in the bank settlement entry."
                ),
                recommendation=RecommendationType.VERIFY_BANK_ENTRY,
                evidence_references=evidence_references,
            )

        if exception_type == "duplicate_settlement":
            return InvestigationResult(
                payment_id=result.payment_id,
                exception_type=exception_type,
                likely_cause=(
                    "Multiple settlement records reference the same "
                    "settlement identifier."
                ),
                confidence=0.99,
                explanation=(
                    "Duplicate settlement records were detected for "
                    "the same settlement identifier. This may indicate "
                    "duplicate processing or duplicated settlement data."
                ),
                recommendation=RecommendationType.REVIEW,
                evidence_references=evidence_references,
            )

        if exception_type == "timing_difference":
            return InvestigationResult(
                payment_id=result.payment_id,
                exception_type=exception_type,
                likely_cause=(
                    "The bank transaction occurred significantly "
                    "later than the settlement."
                ),
                confidence=0.94,
                explanation=(
                    "The settlement exists and the amounts reconcile, "
                    "but the bank transaction falls outside the "
                    "expected timing window."
                ),
                recommendation=RecommendationType.RETRY_RECONCILIATION,
                evidence_references=evidence_references,
            )

        return InvestigationResult(
            payment_id=result.payment_id,
            exception_type=exception_type,
            likely_cause=(
                "The reconciliation exception requires "
                "further investigation."
            ),
            confidence=0.80,
            explanation=(
                "The reconciliation engine identified an exception "
                "that requires further investigation."
            ),
            recommendation=RecommendationType.ESCALATE,
            evidence_references=evidence_references,
        )


class GroqInvestigationProvider(InvestigationProvider):
    """LLM-based investigation provider using Groq."""

    def __init__(self) -> None:
        self.client = Groq(
            api_key=settings.groq_api_key,
            max_retries=0,
        )
        self.model = settings.groq_model

    def investigate(
        self,
        result: ReconciliationResult,
        evidence: list[Evidence],
    ) -> InvestigationResult:

        evidence_references = [
            item.reference for item in evidence
        ]

        evidence_text = "\n".join(
            f"- [{item.source}] {item.reference}: {item.description}"
            for item in evidence
        )

        prompt = f"""
You are a financial reconciliation investigation analyst.

Return the investigation as valid JSON.

Analyze the reconciliation exception using ONLY the supplied
reconciliation result and evidence.

Do not invent transactions, amounts, dates, causes, or evidence.

Reconciliation result:
- Payment ID: {result.payment_id}
- Status: {result.status}
- Exception type: {result.exception_type}
- Expected amount: {result.expected_amount}
- Settled amount: {result.settled_amount}
- Bank amount: {result.bank_amount}
- Difference: {result.difference}

Available evidence:
{evidence_text}

Valid evidence references are:
{json.dumps(evidence_references)}

Return a JSON object containing:
- payment_id
- exception_type
- likely_cause
- confidence
- explanation
- recommendation
- evidence_references

The recommendation MUST be one of:
- review
- retry_reconciliation
- verify_settlement
- verify_bank_entry
- escalate

The confidence must be between 0 and 1.

Evidence references MUST be copied EXACTLY from the valid
evidence reference list.

Do not create new evidence references.

Return ONLY valid JSON.
"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a careful financial investigation "
                        "assistant. Ground every conclusion in evidence. "
                        "Return the investigation as valid JSON."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "investigation_result",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "payment_id": {
                                "type": "string"
                            },
                            "exception_type": {
                                "type": "string"
                            },
                            "likely_cause": {
                                "type": "string"
                            },
                            "confidence": {
                                "type": "number",
                                "minimum": 0,
                                "maximum": 1,
                            },
                            "explanation": {
                                "type": "string"
                            },
                            "recommendation": {
                                "type": "string",
                                "enum": [
                                    "review",
                                    "retry_reconciliation",
                                    "verify_settlement",
                                    "verify_bank_entry",
                                    "escalate",
                                ],
                            },
                            "evidence_references": {
                                "type": "array",
                                "items": {
                                    "type": "string"
                                },
                            },
                        },
                        "required": [
                            "payment_id",
                            "exception_type",
                            "likely_cause",
                            "confidence",
                            "explanation",
                            "recommendation",
                            "evidence_references",
                        ],
                        "additionalProperties": False,
                    },
                },
            },
            temperature=0,
        )

        content = response.choices[0].message.content

        if not content:
            raise ValueError(
                "Groq returned an empty investigation response."
            )

        data = json.loads(content)

        return InvestigationResult.model_validate(data)


class InvestigationAgent:
    """Investigation agent with a safe fallback provider."""

    def __init__(
        self,
        provider: InvestigationProvider,
        fallback_provider: InvestigationProvider | None = None,
    ) -> None:
        self.provider = provider
        self.fallback_provider = fallback_provider

    def investigate(
        self,
        result: ReconciliationResult,
        evidence: list[Evidence],
    ) -> InvestigationResult:
        """Run the primary provider and fall back if it fails."""

        try:
            return self.provider.investigate(
                result,
                evidence,
            )

        except Exception:
            if self.fallback_provider is None:
                raise

            return self.fallback_provider.investigate(
                result,
                evidence,
            )