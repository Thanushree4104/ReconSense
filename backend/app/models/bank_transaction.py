from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.core.enums import BankTransactionType


class BankTransaction(BaseModel):
    """Represents a transaction appearing in the merchant's bank ledger."""

    model_config = ConfigDict(extra="forbid")

    bank_reference: str
    settlement_id: str
    amount: Decimal = Field(gt=0)
    transaction_type: BankTransactionType
    transaction_date: datetime