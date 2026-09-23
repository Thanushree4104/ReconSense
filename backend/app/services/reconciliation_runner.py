from app.core.enums import (
    BankTransactionType,
    PaymentStatus,
    SettlementStatus,
)
from app.db.database import SessionLocal
from app.db.models import EvidenceDB, ReconciliationResultDB
from app.db.repository import (
    BankTransactionRepository,
    PaymentRepository,
    SettlementRepository,
)
from app.models.bank_transaction import BankTransaction
from app.models.payment import Payment
from app.models.settlement import Settlement
from app.services.reconciliation import reconcile_payment


def run_reconciliation() -> list:
    """Run deterministic reconciliation and persist results."""

    db = SessionLocal()

    try:
        payment_repo = PaymentRepository(db)
        settlement_repo = SettlementRepository(db)
        bank_repo = BankTransactionRepository(db)

        db.query(EvidenceDB).delete()
        db.query(ReconciliationResultDB).delete()

        results = []

        for payment_db in payment_repo.list_all():
            payment = Payment(
                payment_id=payment_db.payment_id,
                order_id=payment_db.order_id,
                amount=payment_db.amount,
                currency=payment_db.currency,
                payment_time=payment_db.payment_time,
                status=PaymentStatus(payment_db.status),
                payment_method=payment_db.payment_method,
            )

            settlements = [
                Settlement(
                    settlement_id=settlement.settlement_id,
                    payment_id=settlement.payment_id,
                    gross_amount=settlement.gross_amount,
                    fee=settlement.fee,
                    tax=settlement.tax,
                    net_amount=settlement.net_amount,
                    settlement_date=settlement.settlement_date,
                    status=SettlementStatus(settlement.status),
                )
                for settlement in settlement_repo.get_for_payment(
                    payment.payment_id
                )
            ]

            bank_transactions: list[BankTransaction] = []

            for settlement in settlements:
                bank_records = bank_repo.get_for_settlement(
                    settlement.settlement_id
                )

                bank_transactions.extend(
                    BankTransaction(
                        bank_reference=record.bank_reference,
                        settlement_id=record.settlement_id,
                        amount=record.amount,
                        transaction_type=BankTransactionType(record.transaction_type),
                        transaction_date=record.transaction_date,
                    )
                    for record in bank_records
                )

            result = reconcile_payment(
                payment=payment,
                settlements=settlements,
                bank_transactions=bank_transactions,
            )

            result_db = ReconciliationResultDB(
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

            db.add(result_db)

            for evidence in result.evidence:
                db.add(
                    EvidenceDB(
                        payment_id=result.payment_id,
                        source=evidence.source,
                        reference=evidence.reference,
                        description=evidence.description,
                    )
                )

            results.append(result)

        db.commit()

        return results

    finally:
        db.close()


if __name__ == "__main__":
    for result in run_reconciliation():
        print(
            result.payment_id,
            "->",
            result.status,
            "|",
            result.exception_type,
        )