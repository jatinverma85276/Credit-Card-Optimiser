# app/graph/graph.py
# import sqlite3
# from langgraph.checkpoint.sqlite import SqliteSaver
# from IPython.display import Image, display
from langgraph.graph import StateGraph, END
from app.graph.memory_node.node import memory_retrieval_node, profiler_node
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
    transaction_parser_node,
    manage_request_node
)

# 1. Setup Persistent Checkpointer Connection
# We use a context manager in the main execution block usually, 
# but for a script, we can open it globally or pass it in.
# conn = sqlite3.connect("checkpoints.db", check_same_thread=False)
# memory = SqliteSaver(conn)

# def build_graph():
#     builder = StateGraph(GraphState)

#     builder.add_node("llm", llm_node)
#     builder.set_entry_point("llm")
#     builder.add_edge("llm", END)

#     return builder.compile()

def route_selector(state: GraphState) -> str:
    return state["route"]

def flow_decision_selector(state: GraphState) -> str:
    """Routes based on the supreme manage_request node decision"""
    return state["flow_decision"]

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

def route_after_fetch_cards(state: GraphState) -> Literal["reward_calculation", "__end__"]:
    """
    Decides whether to proceed with reward calculation
    or stop if no cards were found.
    """
    cards = state.get("available_cards", [])
    
    if cards and len(cards) > 0:
        # User has cards, continue to reward calculation
        return "reward_calculation"
    
    # No cards found, stop here
    # The user has already received the "Please add cards..." message
    return "__end__"


def build_graph(memory=None):
    builder = StateGraph(GraphState)

    # Add the supreme routing node
    builder.add_node("manage_request", manage_request_node)
    
    # Legacy nodes (kept for backward compatibility if needed)
    builder.add_node("router", router_node)
    builder.add_node("finance_router", finance_router_node)

    # Card management flow nodes
    builder.add_node("card_parser", card_parser_node)
    builder.add_node("add_card", add_card_node)
    
    # Profiler and memory nodes
    builder.add_node("profiler", profiler_node)
    builder.add_node("memory_retrieval", memory_retrieval_node)
    builder.add_node("memory_retrieval_general", memory_retrieval_node)
    
    # Recommendation flow nodes
    builder.add_node("transaction_parser", transaction_parser_node)
    builder.add_node("fetch_cards", fetch_user_cards_node)
    builder.add_node("reward_calculation", reward_calculation_node)
    builder.add_node("decision", decision_node)
    builder.add_node("llm_recommendation", llm_recommendation_node)
    
    # General agent nodes
    builder.add_node("general_agent", general_llm_node)

    # Set entry point: profiler -> manage_request (supreme router)
    builder.set_entry_point("profiler")
    builder.add_edge("profiler", "manage_request")

    # Supreme routing from manage_request node
    builder.add_conditional_edges(
        "manage_request",
        flow_decision_selector,
        {
            "add_card_flow": "card_parser",
            "recommendation_flow": "transaction_parser",
            "general_flow": "memory_retrieval_general"
        }
    )

    # Add Card Flow: card_parser -> add_card -> END
    builder.add_conditional_edges(
        "card_parser",
        route_after_parser,
        {
            "add_card": "add_card",
            "__end__": END
        }
    )
    builder.add_edge("add_card", END)

    # Recommendation Flow: transaction_parser -> fetch_cards -> (conditional) -> reward_calculation -> decision -> memory_retrieval -> llm_recommendation -> END
    builder.add_edge("transaction_parser", "fetch_cards")
    
    # Conditional edge: only continue if cards were found
    builder.add_conditional_edges(
        "fetch_cards",
        route_after_fetch_cards,
        {
            "reward_calculation": "reward_calculation",
            "__end__": END
        }
    )
    
    builder.add_edge("reward_calculation", "decision")
    builder.add_edge("decision", "memory_retrieval")
    builder.add_edge("memory_retrieval", "llm_recommendation")
    builder.add_edge("llm_recommendation", END)

    # General Flow: memory_retrieval_general -> general_agent -> END
    builder.add_edge("memory_retrieval_general", "general_agent")
    builder.add_edge("general_agent", END)

    graph = builder.compile(checkpointer=memory)

    # graph_png = graph.get_graph().draw_mermaid_png()

    # with open("graph.png", "wb") as f:
    #     f.write(graph_png)

    return graph
    # return builder.compile(checkpointer=memory)