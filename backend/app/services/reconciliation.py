from collections import Counter
from datetime import timedelta
from decimal import Decimal

from app.core.enums import ExceptionType, ReconciliationStatus, SettlementStatus
from app.models.bank_transaction import BankTransaction
from app.models.payment import Payment
from app.models.reconciliation import Evidence, ReconciliationResult
from app.models.settlement import Settlement


def reconcile_payment(
    payment: Payment,
    settlements: list[Settlement],
    bank_transactions: list[BankTransaction],
) -> ReconciliationResult:
    """Reconcile one payment against settlement and bank records."""

    payment_settlements = [
        settlement
        for settlement in settlements
        if settlement.payment_id == payment.payment_id
    ]

    if not payment_settlements:
        return ReconciliationResult(
            payment_id=payment.payment_id,
            status=ReconciliationStatus.EXCEPTION,
            expected_amount=payment.amount,
            exception_type=ExceptionType.MISSING_SETTLEMENT,
            evidence=[
                Evidence(
                    source="settlement",
                    reference=payment.payment_id,
                    description="No settlement record was found for the payment.",
                )
            ],
        )

    settlement_ids = [
        settlement.settlement_id for settlement in payment_settlements
    ]
    settlement_counts = Counter(settlement_ids)

    duplicate_ids = [
        settlement_id
        for settlement_id, count in settlement_counts.items()
        if count > 1
    ]

    if duplicate_ids:
        settled_amount = sum(
            (settlement.net_amount for settlement in payment_settlements),
            Decimal(0),
        )

        return ReconciliationResult(
            payment_id=payment.payment_id,
            status=ReconciliationStatus.EXCEPTION,
            expected_amount=payment.amount,
            settled_amount=settled_amount,
            exception_type=ExceptionType.DUPLICATE_SETTLEMENT,
            evidence=[
                Evidence(
                    source="settlement",
                    reference=settlement_id,
                    description="Settlement record appears more than once.",
                )
                for settlement_id in duplicate_ids
            ],
        )

    if any(
        settlement.status != SettlementStatus.SETTLED
        for settlement in payment_settlements
    ):
        settled_amount = sum(
            (settlement.net_amount for settlement in payment_settlements),
            Decimal(0),
        )

        return ReconciliationResult(
            payment_id=payment.payment_id,
            status=ReconciliationStatus.EXCEPTION,
            expected_amount=payment.amount,
            settled_amount=settled_amount,
            exception_type=ExceptionType.MISSING_SETTLEMENT,
            evidence=[
                Evidence(
                    source="settlement",
                    reference=settlement.settlement_id,
                    description=(
                        f"Settlement status is '{settlement.status}', "
                        "not 'settled'."
                    ),
                )
                for settlement in payment_settlements
            ],
        )

    gross_amount = sum(
        (settlement.gross_amount for settlement in payment_settlements),
        Decimal(0),
    )

    net_amount = sum(
        (settlement.net_amount for settlement in payment_settlements),
        Decimal(0),
    )

    settlement_bank_transactions = [
        transaction
        for transaction in bank_transactions
        if transaction.settlement_id in settlement_ids
    ]

    bank_amount = sum(
        (transaction.amount for transaction in settlement_bank_transactions),
        Decimal(0),
    )

    payment_difference = payment.amount - gross_amount

    if payment_difference != Decimal(0):
        return ReconciliationResult(
            payment_id=payment.payment_id,
            status=ReconciliationStatus.EXCEPTION,
            expected_amount=payment.amount,
            settled_amount=net_amount,
            bank_amount=(
                bank_amount if settlement_bank_transactions else None
            ),
            difference=payment_difference,
            exception_type=ExceptionType.AMOUNT_MISMATCH,
            evidence=[
                Evidence(
                    source="payment",
                    reference=payment.payment_id,
                    description=f"Expected payment amount: {payment.amount}.",
                ),
                Evidence(
                    source="settlement",
                    reference=settlement_ids[0],
                    description=f"Settlement gross amount: {gross_amount}.",
                ),
            ],
        )

    if not settlement_bank_transactions:
        return ReconciliationResult(
            payment_id=payment.payment_id,
            status=ReconciliationStatus.EXCEPTION,
            expected_amount=payment.amount,
            settled_amount=net_amount,
            exception_type=ExceptionType.BANK_MISMATCH,
            evidence=[
                Evidence(
                    source="bank",
                    reference=settlement_ids[0],
                    description="No bank transaction was found for the settlement.",
                )
            ],
        )

    bank_difference = net_amount - bank_amount

    if bank_difference != Decimal(0):
        return ReconciliationResult(
            payment_id=payment.payment_id,
            status=ReconciliationStatus.EXCEPTION,
            expected_amount=payment.amount,
            settled_amount=net_amount,
            bank_amount=bank_amount,
            difference=bank_difference,
            exception_type=ExceptionType.BANK_MISMATCH,
            evidence=[
                Evidence(
                    source="settlement",
                    reference=settlement_ids[0],
                    description=f"Expected bank credit: {net_amount}.",
                ),
                Evidence(
                    source="bank",
                    reference=settlement_bank_transactions[0].bank_reference,
                    description=f"Actual bank amount: {bank_amount}.",
                ),
            ],
        )

    timing_difference = any(
        abs(
            (
                transaction.transaction_date
                - next(
                    settlement.settlement_date
                    for settlement in payment_settlements
                    if settlement.settlement_id == transaction.settlement_id
                )
            ).total_seconds()
        )
        > timedelta(days=1).total_seconds()
        for transaction in settlement_bank_transactions
    )

    if timing_difference:
        return ReconciliationResult(
            payment_id=payment.payment_id,
            status=ReconciliationStatus.EXCEPTION,
            expected_amount=payment.amount,
            settled_amount=net_amount,
            bank_amount=bank_amount,
            exception_type=ExceptionType.TIMING_DIFFERENCE,
            evidence=[
                Evidence(
                    source="settlement",
                    reference=settlement_ids[0],
                    description=(
                        "Bank transaction occurred outside the expected "
                        "one-day settlement window."
                    ),
                )
            ],
        )

    return ReconciliationResult(
        payment_id=payment.payment_id,
        status=ReconciliationStatus.MATCHED,
        expected_amount=payment.amount,
        settled_amount=net_amount,
        bank_amount=bank_amount,
        difference=Decimal(0),
        evidence=[
            Evidence(
                source="payment",
                reference=payment.payment_id,
                description="Payment amount matched settlement gross amount.",
            ),
            Evidence(
                source="settlement",
                reference=settlement_ids[0],
                description="Settlement net amount matched bank transaction.",
            ),
            Evidence(
                source="bank",
                reference=settlement_bank_transactions[0].bank_reference,
                description="Bank transaction confirmed the settlement amount.",
            ),
        ],
    )