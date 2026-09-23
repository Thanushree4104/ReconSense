
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import (
    AuditEventDB,
    BankTransactionDB,
    EvidenceDB,
    PaymentDB,
    SettlementDB,
)


class PaymentRepository:
    """Database operations for payments."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, payment: PaymentDB) -> PaymentDB:
        self.db.add(payment)
        self.db.commit()
        self.db.refresh(payment)
        return payment

    def get(self, payment_id: str) -> PaymentDB | None:
        return self.db.get(PaymentDB, payment_id)

    def list_all(self) -> list[PaymentDB]:
        statement = select(PaymentDB)
        return list(self.db.scalars(statement).all())


class SettlementRepository:
    """Database operations for settlements."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, settlement: SettlementDB) -> SettlementDB:
        self.db.add(settlement)
        self.db.commit()
        self.db.refresh(settlement)
        return settlement

    def get(self, settlement_id: str) -> SettlementDB | None:
        statement = select(SettlementDB).where(
            SettlementDB.settlement_id == settlement_id
    )
        return self.db.scalars(statement).first()

    def get_for_payment(self, payment_id: str) -> list[SettlementDB]:
        statement = select(SettlementDB).where(
            SettlementDB.payment_id == payment_id
        )
        return list(self.db.scalars(statement).all())


class BankTransactionRepository:
    """Database operations for bank transactions."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, transaction: BankTransactionDB) -> BankTransactionDB:
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        return transaction

    def get(self, bank_reference: str) -> BankTransactionDB | None:
        statement = select(BankTransactionDB).where(
            BankTransactionDB.bank_reference == bank_reference
    )
        return self.db.scalars(statement).first()

    def get_for_settlement(
        self,
        settlement_id: str,
    ) -> list[BankTransactionDB]:
        statement = select(BankTransactionDB).where(
            BankTransactionDB.settlement_id == settlement_id
        )
        return list(self.db.scalars(statement).all())
class EvidenceRepository:
    """Database operations for reconciliation evidence."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, evidence: EvidenceDB) -> EvidenceDB:
        self.db.add(evidence)
        self.db.commit()
        self.db.refresh(evidence)
        return evidence

    def get_for_payment(self, payment_id: str) -> list[EvidenceDB]:
        statement = select(EvidenceDB).where(
            EvidenceDB.payment_id == payment_id
        )
        return list(self.db.scalars(statement).all())

class AuditEventRepository:
    """Database operations for audit events."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, event: AuditEventDB) -> AuditEventDB:
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

    def get_for_payment(self, payment_id: str) -> list[AuditEventDB]:
        statement = (
            select(AuditEventDB)
            .where(AuditEventDB.payment_id == payment_id)
            .order_by(AuditEventDB.created_at)
        )
        return list(self.db.scalars(statement).all())
    def exists_for_payment_and_type(
        self,
        payment_id: str,
        event_type: str,
    ) -> bool:
        """Check whether an audit event of this type already exists."""
        statement = (
            select(AuditEventDB)
            .where(
                AuditEventDB.payment_id == payment_id,
                AuditEventDB.event_type == event_type,
            )
            .limit(1)
        )

        return self.db.scalars(statement).first() is not None