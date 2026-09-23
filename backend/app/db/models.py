from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class PaymentDB(Base):
    """Database representation of a payment."""

    __tablename__ = "payments"

    payment_id: Mapped[str] = mapped_column(
        String(50),
        primary_key=True,
    )
    order_id: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        nullable=False,
    )
    currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
    )
    payment_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )
    payment_method: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )


class SettlementDB(Base):
    """Database representation of a settlement."""

    __tablename__ = "settlements"
    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )
    settlement_id: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )
    payment_id: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )
    gross_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        nullable=False,
    )
    fee: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        nullable=False,
    )
    tax: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        nullable=False,
    )
    net_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        nullable=False,
    )
    settlement_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )


class BankTransactionDB(Base):
    """Database representation of a bank transaction."""

    __tablename__ = "bank_transactions"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        )
    bank_reference: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
        index=True,
        )
    settlement_id: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        nullable=False,
    )
    transaction_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )
    transaction_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
class ReconciliationResultDB(Base):
    """Database representation of a reconciliation result."""

    __tablename__ = "reconciliation_results"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )
    payment_id: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )
    expected_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        nullable=False,
    )
    settled_amount: Mapped[Decimal | None] = mapped_column(
        Numeric(18, 2),
        nullable=True,
    )
    bank_amount: Mapped[Decimal | None] = mapped_column(
        Numeric(18, 2),
        nullable=True,
    )
    difference: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        nullable=False,
    )
    exception_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )


class EvidenceDB(Base):
    """Database representation of reconciliation evidence."""

    __tablename__ = "evidence"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )
    payment_id: Mapped[str,] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )
    source: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )
    reference: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    description: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )
class AuditEventDB(Base):
    __tablename__ = "audit_events"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )
    payment_id: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )
    event_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    actor: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    description: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )