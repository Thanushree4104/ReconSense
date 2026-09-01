from enum import StrEnum


class PaymentStatus(StrEnum):
    CAPTURED = "captured"
    FAILED = "failed"
    REVERSED = "reversed"
    REFUNDED = "refunded"


class SettlementStatus(StrEnum):
    PENDING = "pending"
    SETTLED = "settled"
    FAILED = "failed"


class BankTransactionType(StrEnum):
    CREDIT = "credit"
    DEBIT = "debit"


class ReconciliationStatus(StrEnum):
    MATCHED = "matched"
    EXCEPTION = "exception"
    UNRESOLVED = "unresolved"


class ExceptionType(StrEnum):
    AMOUNT_MISMATCH = "amount_mismatch"
    MISSING_SETTLEMENT = "missing_settlement"
    BANK_MISMATCH = "bank_mismatch"
    DUPLICATE_SETTLEMENT = "duplicate_settlement"
    TIMING_DIFFERENCE = "timing_difference"
    REFUND_DIFFERENCE = "refund_difference"
    UNKNOWN = "unknown"