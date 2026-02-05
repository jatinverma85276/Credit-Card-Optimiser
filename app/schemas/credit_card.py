from typing import List, Optional, Union
from pydantic import BaseModel, Field

class RewardRule(BaseModel):
    category: str = Field(..., description="E.g., '10X Partners - Group A', '5X Partners'")
    multiplier: str = Field(..., description="The multiplier or cashback % (e.g., '10X', '5%')")
    reward_rate_description: Optional[str] = Field(None, description="E.g., 'Points per Rs. 50 spent'")
    merchants: List[str] = Field(..., description="List of specific merchants or 'All'")
    cap: Optional[str] = Field(None, description="Max points/cashback per period. Mention if shared across merchants.")
    period: Optional[str] = Field(None, description="E.g., 'Month', 'Year', 'Statement Cycle'")

class Milestone(BaseModel):
    spend_threshold: str = Field(..., description="Amount required to unlock reward (e.g., 'Rs. 1.20 Lakhs')")
    reward: str = Field(..., description="What is given (e.g., 'Rs. 500 Gift Voucher')")
    period: str = Field(..., description="Timeframe to reach spend (e.g., 'Annual', 'Monthly')")

class Eligibility(BaseModel):
    min_income_salaried: Optional[str] = None
    min_income_self_employed: Optional[str] = None
    age_requirement: Optional[str] = None
    location_constraints: Optional[List[str]] = Field(None, description="List of eligible cities/regions")
    other_conditions: Optional[List[str]] = Field(None, description="E.g., 'Company trading > 12 months'")

class CreditCard(BaseModel):
    extracted_from_user: bool = Field(..., description="Set to FALSE if the user input was empty, generic, or lacked specific card details.")
    card_name: str
    issuer: str
    card_type: str
    annual_fee: str
    fee_waiver_condition: Optional[str]
    welcome_bonus: Optional[str]
    
    # Nested Complex Objects
    reward_program_name: Optional[str]
    reward_rules: List[RewardRule]
    milestone_benefits: List[Milestone] = Field(default_factory=list)
    eligibility_criteria: Optional[Eligibility]
    
    # Lists
    excluded_categories: List[str]
    key_benefits: List[str]
    
    # Nuance handling
    liability_policy: Optional[str] = Field(None, description="Zero liability conditions")