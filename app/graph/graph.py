# app/graph/graph.py

from langgraph.graph import StateGraph, END
from app.graph.state import GraphState
from app.graph.nodes import (
    add_card_node,
    card_parser_node,
    expense_decision_node,
    finance_router_node,
    router_node,
    general_llm_node
)

# def build_graph():
#     builder = StateGraph(GraphState)

#     builder.add_node("llm", llm_node)
#     builder.set_entry_point("llm")
#     builder.add_edge("llm", END)

#     return builder.compile()

def route_selector(state: GraphState) -> str:
    return state["route"]

def finance_route_selector(state: GraphState) -> str:
    return state["finance_route"]


def build_graph():
    builder = StateGraph(GraphState)

    builder.add_node("router", router_node)
    builder.add_node("finance_router", finance_router_node)

    builder.add_node("card_parser", card_parser_node)
    builder.add_node("add_card", add_card_node)
    
    builder.add_node("finance_expense", expense_decision_node)
    builder.add_node("general_agent", general_llm_node)

    builder.set_entry_point("router")

    # Level 1 routing
    builder.add_conditional_edges(
        "router",
        route_selector,
        {
            "finance": "finance_router",
            "general": "general_agent"
        }
    )

    # Level 2 routing (inside finance)
    builder.add_conditional_edges(
        "finance_router",
        finance_route_selector,
        {
            "add_card": "card_parser",
            "expense": "finance_expense"
        }
    )
    
    builder.add_edge("card_parser", "add_card")
    builder.add_edge("add_card", END)
    builder.add_edge("finance_expense", END)
    builder.add_edge("general_agent", END)

    return builder.compile()