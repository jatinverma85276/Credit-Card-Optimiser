from typing import Any, Optional, TypedDict, List, Literal, Dict, Annotated
# from langchain_core.messages import BaseMessage
from app.schemas.transaction import Transaction
from langgraph.graph.message import add_messages # <--- KEY IMPORT

class GraphState(TypedDict):
    # 'add_messages' tells LangGraph: "Don't replace the list. Append new messages to it."
    messages: Annotated[list, add_messages]
    # messages: List[BaseMessage]

    # User identification
    user_id: str  # User ID for personalization

    # top-level routing
    route: Literal["finance", "general"]

    # finance sub-routing
    finance_route: Literal["add_card", "expense"]

    flow_decision: Literal["add_card_flow", "recommendation_flow", "general_flow"]

    parsed_card: Optional[Dict[str, Any]]

    parsed_transaction: Optional[Transaction]

    available_cards: Optional[List[Dict[str, Any]]]

    best_card: Optional[dict]
    reward_breakdown: Optional[list]

    memory_context: str

