from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from uuid import uuid4
from datetime import datetime
from app.models.expense import Expense
from app.models.card import CreditCard
from typing import List, Optional

class Message(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class AgentState(BaseModel):
    session_id: str = Field(default_factory=lambda: str(uuid4()))
    raw_message: Optional[str] = None
    expense: Optional[Expense] = None
    cards: List[CreditCard] = []
    card_stats: Dict[str, Any] = {}
    simulations: List[Dict[str, Any]] = []
    recommendation: Optional[Dict[str, Any]] = None
    conversation_history: List[Message] = Field(default_factory=list)
    
    def add_user_message(self, message: str):
        self.conversation_history.append(Message(role="user", content=message))
    
    def add_assistant_message(self, message: str):
        self.conversation_history.append(Message(role="assistant", content=message))
    
    def get_conversation_context(self) -> str:
        return "\n".join(
            f"{msg.role.upper()}: {msg.content}" 
            for msg in self.conversation_history[-10:]  # Last 10 messages for context
        )
