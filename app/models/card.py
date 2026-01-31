from pydantic import BaseModel
from typing import Optional, Dict


class CashbackRule(BaseModel):
    category: str
    percentage: float
    monthly_cap: Optional[float] = None


class RewardRule(BaseModel):
    category: str
    points_per_rupee: float
    point_value_rupee: float  # conversion value


class CreditCard(BaseModel):
    card_id: str
    card_name: str
    card_type: str  # "cashback" | "reward"
    cashback_rules: Optional[Dict[str, CashbackRule]] = None
    reward_rules: Optional[Dict[str, RewardRule]] = None
