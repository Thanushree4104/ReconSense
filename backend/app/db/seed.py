from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal

from app.db.database import SessionLocal
from app.db.models import (
    BankTransactionDB,
    PaymentDB,
    SettlementDB,
)


def money(value: float | str | Decimal) -> Decimal:
    """Convert a numeric value to Decimal for financial fields."""
    return Decimal(str(value)).quantize(Decimal("0.01"))


def seed_database() -> None:
    db = SessionLocal()

    try:
        # ---------------------------------------------------------
        # CLEAR EXISTING DATA
        # ---------------------------------------------------------
        # Delete children first because of foreign-key relationships.
        db.query(BankTransactionDB).delete()
        db.query(SettlementDB).delete()
        db.query(PaymentDB).delete()
        db.commit()

        # ---------------------------------------------------------
        # BATCH CONFIGURATION
        # ---------------------------------------------------------
        TOTAL_PAYMENTS = 100

        # Exactly 30 exceptions.
        AMOUNT_MISMATCH_IDS = {
            2,
            21,
            22,
            23,
            24,
            25,
            26,
        }

        MISSING_SETTLEMENT_IDS = {
            3,
            31,
            32,
            33,
            34,
            35,
        }

        BANK_MISMATCH_IDS = {
            4,
            41,
            42,
            43,
            44,
            45,
            46,
            47,
        }

        DUPLICATE_SETTLEMENT_IDS = {
            5,
            51,
            52,
            53,
        }

        TIMING_DIFFERENCE_IDS = {
            6,
            61,
            62,
            63,
            64,
        }

        exception_ids = (
            AMOUNT_MISMATCH_IDS
            | MISSING_SETTLEMENT_IDS
            | BANK_MISMATCH_IDS
            | DUPLICATE_SETTLEMENT_IDS
            | TIMING_DIFFERENCE_IDS
        )

        assert len(exception_ids) == 30

        # ---------------------------------------------------------
        # CREATE PAYMENTS
        # ---------------------------------------------------------
        payments: list[PaymentDB] = []

        base_time = datetime(2026, 9, 1, 10, 0, 0, tzinfo=UTC)

        for i in range(1, TOTAL_PAYMENTS + 1):
            payment_id = f"PAY_{i:03d}"
            order_id = f"ORDER_{i:03d}"

            # Deterministic but varied payment amounts.
            amount = money(500 + ((i * 137) % 4500))

            payment_time = base_time + timedelta(
                minutes=i * 7
            )

            payment = PaymentDB(
                payment_id=payment_id,
                order_id=order_id,
                amount=amount,
                currency="INR",
                payment_time=payment_time,
                status="captured",
                payment_method="upi",
            )

            payments.append(payment)

        db.add_all(payments)
        db.flush()

        # ---------------------------------------------------------
        # CREATE SETTLEMENTS + BANK TRANSACTIONS
        # ---------------------------------------------------------
        settlements: list[SettlementDB] = []
        bank_transactions: list[BankTransactionDB] = []

        for i in range(1, TOTAL_PAYMENTS + 1):
            payment_id = f"PAY_{i:03d}"
            settlement_id = f"SET_{i:03d}"

            payment_amount = money(
                500 + ((i * 137) % 4500)
            )

            payment_time = base_time + timedelta(
                minutes=i * 7
            )

            settlement_time = payment_time + timedelta(
                hours=2
            )

            # -----------------------------------------------------
            # CASE 1: MISSING SETTLEMENT
            # -----------------------------------------------------
            if i in MISSING_SETTLEMENT_IDS:
                # Deliberately create no settlement and no bank
                # transaction. This represents an unresolved /
                # missing settlement scenario.
                continue

            # -----------------------------------------------------
            # DEFAULT FINANCIAL VALUES
            # -----------------------------------------------------
            gross_amount = payment_amount
            fee = money(20 + (i % 10))
            tax = money(fee * Decimal("0.18"))
            net_amount = money(
                gross_amount - fee - tax
            )

            # -----------------------------------------------------
            # CASE 2: AMOUNT MISMATCH
            # -----------------------------------------------------
            if i in AMOUNT_MISMATCH_IDS:
                # Settlement gross differs from payment amount.
                gross_amount = money(
                    payment_amount - money(50 + (i % 5) * 10)
                )

                net_amount = money(
                    gross_amount - fee - tax
                )

            # -----------------------------------------------------
            # CASE 3: BANK MISMATCH
            # -----------------------------------------------------
            bank_amount = net_amount

            if i in BANK_MISMATCH_IDS:
                # Bank credit differs from expected settlement net.
                bank_amount = money(
                    net_amount - money(50 + (i % 4) * 10)
                )

            # -----------------------------------------------------
            # CASE 4: TIMING DIFFERENCE
            # -----------------------------------------------------
            bank_time = settlement_time + timedelta(
                hours=2
            )

            if i in TIMING_DIFFERENCE_IDS:
                # More than one day after settlement.
                bank_time = settlement_time + timedelta(
                    days=2
                )

            # -----------------------------------------------------
            # CREATE SETTLEMENT
            # -----------------------------------------------------
            settlement = SettlementDB(
                settlement_id=settlement_id,
                payment_id=payment_id,
                gross_amount=gross_amount,
                fee=fee,
                tax=tax,
                net_amount=net_amount,
                settlement_date=settlement_time,
                status="settled",
            )

            settlements.append(settlement)

            # -----------------------------------------------------
            # DUPLICATE SETTLEMENT
            # -----------------------------------------------------
            if i in DUPLICATE_SETTLEMENT_IDS:
                # Two settlement records intentionally use the
                # same settlement ID. The reconciliation engine
                # should detect this as a duplicate settlement.
                duplicate_settlement = SettlementDB(
                    settlement_id=settlement_id,
                    payment_id=payment_id,
                    gross_amount=gross_amount,
                    fee=fee,
                    tax=tax,
                    net_amount=net_amount,
                    settlement_date=settlement_time,
                    status="settled",
                )

                settlements.append(duplicate_settlement)

            # -----------------------------------------------------
            # BANK TRANSACTION
            # -----------------------------------------------------
            bank_transaction = BankTransactionDB(
                bank_reference=f"BANK_{i:03d}",
                settlement_id=settlement_id,
                amount=bank_amount,
                transaction_type="credit",
                transaction_date=bank_time,
            )

            bank_transactions.append(bank_transaction)

        # ---------------------------------------------------------
        # PERSIST
        # ---------------------------------------------------------
        db.add_all(settlements)
        db.add_all(bank_transactions)
        db.commit()

        # ---------------------------------------------------------
        # SUMMARY
        # ---------------------------------------------------------
        payment_count = db.query(PaymentDB).count()
        settlement_count = db.query(SettlementDB).count()
        bank_count = db.query(BankTransactionDB).count()

        print()
        print("=" * 60)
        print("ReconSense Synthetic Batch")
        print("=" * 60)
        print(f"Payments:          {payment_count}")
        print(f"Settlements:       {settlement_count}")
        print(f"Bank transactions: {bank_count}")
        print(f"Expected records:  {TOTAL_PAYMENTS}")
        print(f"Expected exceptions: {len(exception_ids)}")
        print("=" * 60)

        print()
        print("Exception distribution:")
        print(
            f"  Amount mismatch:       "
            f"{len(AMOUNT_MISMATCH_IDS)}"
        )
        print(
            f"  Missing settlement:    "
            f"{len(MISSING_SETTLEMENT_IDS)}"
        )
        print(
            f"  Bank mismatch:         "
            f"{len(BANK_MISMATCH_IDS)}"
        )
        print(
            f"  Duplicate settlement:  "
            f"{len(DUPLICATE_SETTLEMENT_IDS)}"
        )
        print(
            f"  Timing difference:      "
            f"{len(TIMING_DIFFERENCE_IDS)}"
        )
        print(
            f"  Total exceptions:      "
            f"{len(exception_ids)}"
        )
        print(
            f"  Expected matched:      "
            f"{TOTAL_PAYMENTS - len(exception_ids)}"
        )
        print()

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()