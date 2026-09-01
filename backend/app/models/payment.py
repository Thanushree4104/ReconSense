from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.core.enums import PaymentStatus


class Payment(BaseModel):
    """Represents a payment captured by the merchant/payment system."""

    model_config = ConfigDict(extra="forbid")

    payment_id: str
    order_id: str
    amount: Decimal = Field(gt=0)
    currency: str = Field(min_length=3, max_length=3)
    payment_time: datetime
    status: PaymentStatus
    payment_method: str