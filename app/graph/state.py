from typing import Any, Optional, TypedDict, List, Literal, Dict
from langchain_core.messages import BaseMessage
from app.schemas.transaction import Transaction

class GraphState(TypedDict):
    messages: List[BaseMessage]

    # top-level routing
    route: Literal["finance", "general"]

    # finance sub-routing
    finance_route: Literal["add_card", "expense"]

    parsed_card: Optional[Dict[str, Any]]

    parsed_transaction: Optional[Transaction]

    available_cards: Optional[List[Dict[str, Any]]]

    best_card: Optional[dict]
    reward_breakdown: Optional[list]

