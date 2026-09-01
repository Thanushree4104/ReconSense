from datetime import datetime, timezone
from decimal import Decimal

from app.core.enums import (
    BankTransactionType,
    PaymentStatus,
    ReconciliationStatus,
    SettlementStatus,
)
from app.models.bank_transaction import BankTransaction
from app.models.payment import Payment
from app.models.settlement import Settlement
from app.services.reconciliation import reconcile_payment


def create_payment(amount: str = "1000.00") -> Payment:
    return Payment(
        payment_id="PAY_001",
        order_id="ORD_001",
        amount=Decimal(amount),
        currency="INR",
        payment_time=datetime(2026, 9, 1, 10, 0, tzinfo=timezone.utc),
        status=PaymentStatus.CAPTURED,
        payment_method="upi",
    )


def create_settlement(
    gross_amount: str = "1000.00",
    net_amount: str = "982.30",
) -> Settlement:
    return Settlement(
        settlement_id="SET_001",
        payment_id="PAY_001",
        gross_amount=Decimal(gross_amount),
        fee=Decimal("15.00"),
        tax=Decimal("2.70"),
        net_amount=Decimal(net_amount),
        settlement_date=datetime(2026, 9, 2, 10, 0, tzinfo=timezone.utc),
        status=SettlementStatus.SETTLED,
    )


def create_bank_transaction(amount: str = "982.30") -> BankTransaction:
    return BankTransaction(
        bank_reference="BANK_001",
        settlement_id="SET_001",
        amount=Decimal(amount),
        transaction_type=BankTransactionType.CREDIT,
        transaction_date=datetime(2026, 9, 2, 11, 0, tzinfo=timezone.utc),
    )


def test_successful_reconciliation():
    payment = create_payment()
    settlement = create_settlement()
    bank_transaction = create_bank_transaction()

    result = reconcile_payment(
        payment,
        [settlement],
        [bank_transaction],
    )

    assert result.status == ReconciliationStatus.MATCHED
    assert result.exception_type is None
    assert result.difference == Decimal("0")


def test_detects_settlement_amount_mismatch():
    payment = create_payment(amount="1000.00")
    settlement = create_settlement(gross_amount="950.00")
    bank_transaction = create_bank_transaction(amount="932.30")

    result = reconcile_payment(
        payment,
        [settlement],
        [bank_transaction],
    )

    assert result.status == ReconciliationStatus.EXCEPTION
    assert result.exception_type is not None
    assert result.expected_amount == Decimal("1000.00")


def test_detects_missing_settlement():
    payment = create_payment()

    result = reconcile_payment(
        payment,
        [],
        [],
    )

    assert result.status == ReconciliationStatus.EXCEPTION
    assert result.exception_type is not None