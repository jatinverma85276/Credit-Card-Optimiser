from sqlalchemy import Column, Integer, String, Text, JSON, Float, DateTime
from app.db.database import Base
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector  # <--- The Bridge between Python & Postgres
# from pgvector.sqlalchemy import Vector  # <--- The magic import

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



class TransactionHistory(Base):
    __tablename__ = "transaction_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    
    # Standard Fields
    merchant = Column(String)           # e.g., "Uber"
    category = Column(String)           # e.g., "Travel"
    amount = Column(Float)              # e.g., 450.0
    description = Column(Text)          # e.g., "Ride to Airport"
    
    # 🧠 Semantic Brain
    # 1536 is the standard dimension size for OpenAI's 'text-embedding-3-small'
    embedding = Column(Vector(1536)) 

    created_at = Column(DateTime(timezone=True), server_default=func.now())


class UserMemory(Base):
    __tablename__ = "user_memories"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    
    # "My dog's name is Bruno"
    memory_text = Column(Text)
    
    # "identity", "preference", "relationship"
    category = Column(String) 
    
    # 🧠 Semantic Brain (Vector)
    embedding = Column(Vector(1536)) 

    created_at = Column(DateTime(timezone=True), server_default=func.now())


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True)  # External user ID from frontend
    name = Column(String)
    email = Column(String, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class ChatThread(Base):
    __tablename__ = "chat_threads"

    id = Column(Integer, primary_key=True, index=True)
    thread_id = Column(String, unique=True, index=True)
    user_id = Column(String, index=True)  # Link to User
    thread_name = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())