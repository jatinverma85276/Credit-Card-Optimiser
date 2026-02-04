import json
from sqlalchemy.orm import Session
from app.db.models import CreditCardModel
from app.schemas.credit_card import CreditCard

def add_card(db: Session, card: CreditCard):
    db_card = CreditCardModel(
        card_name=card.card_name,
        issuer=card.issuer,
        card_type=card.card_type,
        annual_fee=card.annual_fee,
        fee_waiver_condition=card.fee_waiver_condition,
        welcome_bonus=card.welcome_bonus,
        
        # --- New Simple Field ---
        liability_policy=card.liability_policy,

        # --- Renamed Field ---
        # "reward_program" in Schema -> "reward_program_name" in DB
        reward_program_name=card.reward_program_name,

        # --- JSON Fields --- 
        # Note: If using Pydantic v2, use .model_dump(). 
        # If using Pydantic v1, use .dict().
        
        # Convert List[RewardRule] -> List[dict]
        reward_rules=[r.model_dump() for r in card.reward_rules],
        
        # Convert List[Milestone] -> List[dict]
        milestone_benefits=[m.model_dump() for m in card.milestone_benefits],
        
        # Convert Eligibility object -> dict (handle None case)
        eligibility_criteria=card.eligibility_criteria.model_dump() if card.eligibility_criteria else None,
        
        # Simple Lists (SQLAlchemy JSON column handles List[str] automatically)
        excluded_categories=card.excluded_categories,
        key_benefits=card.key_benefits
    )
    
    db.add(db_card)
    db.commit()
    db.refresh(db_card)
    return db_card