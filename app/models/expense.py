from pydantic import BaseModel
from datetime import datetime


class Expense(BaseModel):
    amount: float
    category: str
    merchant: str
    timestamp: datetime = datetime.utcnow()
