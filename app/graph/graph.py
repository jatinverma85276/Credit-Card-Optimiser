# app/graph/graph.py
import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import StateGraph, END
from app.graph.state import GraphState
from typing import Literal
from app.graph.nodes import (
    add_card_node,
    card_parser_node,
    decision_node,
    expense_decision_node,
    fetch_user_cards_node,
    finance_router_node,
    llm_recommendation_node,
    reward_calculation_node,
    router_node,
    general_llm_node,
    transaction_parser_node
)

# 1. Setup Persistent Checkpointer Connection
# We use a context manager in the main execution block usually, 
# but for a script, we can open it globally or pass it in.
conn = sqlite3.connect("checkpoints.db", check_same_thread=False)
memory = SqliteSaver(conn)

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

def route_after_parser(state: GraphState) -> Literal["add_card", "__end__"]:
    """
    Decides whether to proceed to adding the card to DB 
    or stop if parsing failed/was skipped.
    """
    if state.get("parsed_card"):
        return "add_card"
    
    # If None (because input was empty or invalid), stop here.
    # The user has already received the "Please paste details..." message.
    return "__end__"


def build_graph():
    builder = StateGraph(GraphState)

    builder.add_node("router", router_node)
    builder.add_node("finance_router", finance_router_node)

    builder.add_node("card_parser", card_parser_node)
    builder.add_node("add_card", add_card_node)
    
    builder.add_node("finance_expense", expense_decision_node)
    builder.add_node("general_agent", general_llm_node)

    builder.add_node("transaction_parser", transaction_parser_node)
    builder.add_node("fetch_cards", fetch_user_cards_node)
    builder.add_node("reward_calculation", reward_calculation_node)
    builder.add_node("decision", decision_node)
    builder.add_node("llm_recommendation", llm_recommendation_node)

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

    builder.add_conditional_edges(
        "card_parser",          # From this node
        route_after_parser,     # Run this logic
        {                       # Map logic output to next node
            "add_card": "add_card",
            "__end__": END
        }
    )
    
    builder.add_edge("finance_expense", "transaction_parser")
    builder.add_edge("transaction_parser", "fetch_cards")
    builder.add_edge("fetch_cards", "reward_calculation")
    builder.add_edge("reward_calculation", "decision")
    builder.add_edge("decision", "llm_recommendation")
    builder.add_edge("llm_recommendation", END)

    # builder.add_edge("card_parser", "add_card")
    # builder.add_edge("add_card", END)
    builder.add_edge("general_agent", END)

    return builder.compile(checkpointer=memory)