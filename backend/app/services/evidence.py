from app.db.models import EvidenceDB
from app.db.repository import EvidenceRepository
from app.models.reconciliation import Evidence


class EvidenceService:
    """Service for retrieving structured reconciliation evidence."""

    def __init__(self, repository: EvidenceRepository) -> None:
        self.repository = repository

    def get_for_payment(self, payment_id: str) -> list[Evidence]:
        """Return evidence for a payment as domain models."""

        records = self.repository.get_for_payment(payment_id)

        return [
            Evidence(
                source=record.source,
                reference=record.reference,
                description=record.description,
            )
            for record in records
        ]

    def save(self, payment_id: str, evidence: Evidence) -> Evidence:
        """Persist one evidence record and return the domain model."""

        record = EvidenceDB(
            payment_id=payment_id,
            source=evidence.source,
            reference=evidence.reference,
            description=evidence.description,
        )

        self.repository.create(record)

        return evidence