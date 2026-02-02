from sqlalchemy import Column, Integer, String, Text, JSON
from app.db.database import Base

class CreditCardModel(Base):
    __tablename__ = "credit_cards"

    id = Column(Integer, primary_key=True, index=True)
    
    # --- Basic Info ---
    card_name = Column(String, unique=True, index=True)
    issuer = Column(String, index=True)
    card_type = Column(String)
    annual_fee = Column(String)
    
    # --- Financial Nuances ---
    # Stores the raw text condition, e.g., "Spend 40k to waive"
    fee_waiver_condition = Column(Text, nullable=True)  
    welcome_bonus = Column(Text, nullable=True)
    liability_policy = Column(Text, nullable=True)      # New: "Zero liability if reported < 3 days"

    # --- Complex Nested Data (Stored as JSON) ---
    # Fixed: changed from raw String to Column(String)
    reward_program_name = Column(String, nullable=True) 
    
    # Stores List[RewardRule]
    # Example: [{"category": "10X", "merchants": ["Zomato"], "cap": "500 pts"}]
    reward_rules = Column(JSON, nullable=True)          
    
    # Stores List[Milestone] - New Field
    # Example: [{"spend": "1.2L", "reward": "500 Voucher"}]
    milestone_benefits = Column(JSON, nullable=True)    

    # Stores Eligibility Object - New Field
    # Example: {"income": "4.5L", "cities": ["Delhi", "Mumbai"]}
    eligibility_criteria = Column(JSON, nullable=True)  

    # Stores List[str]
    excluded_categories = Column(JSON, nullable=True)   
    key_benefits = Column(JSON, nullable=True)