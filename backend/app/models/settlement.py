from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.core.enums import SettlementStatus


class Settlement(BaseModel):
    """Represents the processor's settlement record for a payment."""

    model_config = ConfigDict(extra="forbid")

    settlement_id: str
    payment_id: str
    gross_amount: Decimal = Field(gt=0)
    fee: Decimal = Field(ge=0)
    tax: Decimal = Field(ge=0)
    net_amount: Decimal = Field(gt=0)
    settlement_date: datetime
    status: SettlementStatus