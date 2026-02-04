from pydantic import BaseModel, Field
from typing import Optional


class Transaction(BaseModel):
    amount: float = Field(description="Transaction amount in INR")
    merchant: str = Field(description="Merchant name like Amazon, Swiggy, Uber")
    category: Optional[str] = Field(
        default=None,
        description="Category such as food, travel, shopping, fuel etc."
    )
