from datetime import UTC, datetime

from app.db.models import AuditEventDB
from app.db.repository import AuditEventRepository


class AuditService:
    """Service for recording and retrieving audit events."""

    def __init__(self, repository: AuditEventRepository) -> None:
        self.repository = repository

    def record(
        self,
        payment_id: str,
        event_type: str,
        actor: str,
        description: str,
    ) -> AuditEventDB | None:
        """Record an audit event if it has not already been recorded."""

        if self.repository.exists_for_payment_and_type(
            payment_id,
            event_type,
        ):
            return None

        event = AuditEventDB(
            payment_id=payment_id,
            event_type=event_type,
            actor=actor,
            description=description,
            created_at=datetime.now(UTC),
        )

        return self.repository.create(event)

    def get_for_payment(
        self,
        payment_id: str,
    ) -> list[AuditEventDB]:
        """Return audit events for a payment."""
        return self.repository.get_for_payment(payment_id)