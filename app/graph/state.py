from typing import Any, Optional, TypedDict, List, Literal, Dict
from langchain_core.messages import BaseMessage

class GraphState(TypedDict):
    messages: List[BaseMessage]

    # top-level routing
    route: Literal["finance", "general"]

    # finance sub-routing
    finance_route: Literal["add_card", "expense"]

    parsed_card: Optional[Dict[str, Any]]
