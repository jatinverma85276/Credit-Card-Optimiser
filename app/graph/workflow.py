from app.llm.client import get_llm
from app.llm.prompts import CARD_INGEST_PROMPT, FORMAT_RECOMMENDATION_PROMPT, PARSE_EXPENSE_PROMPT
from app.models.expense import Expense
from langgraph.graph import StateGraph, END
from app.models.state import AgentState
from app.utils.category_mapper import normalize_category
import json

# -------- Nodes -------- #
def llm_parse_expense_node(state):
    llm = get_llm()

    response = llm.invoke(
        PARSE_EXPENSE_PROMPT.format_messages(
            message=state.raw_message
        )
    )

    data = json.loads(response.content)

    state.expense = Expense(
        amount=data["amount"],
        merchant=data["merchant"],
        category=data["category"]
    )

    return state

def input_expense_node(state: AgentState):
    # Expense already injected
    return state


def load_cards_node(state: AgentState):
    # TEMP: hardcoded cards (we'll move this to DB later)
    from app.data.card import CARDS
    state.cards = CARDS
    return state



def load_memory_node(state: AgentState):
    from app.memory.store import MemoryStore
    store = MemoryStore()
    state.card_stats = store.get_card_stats()
    return state


def normalize_expense_node(state):
    state.expense.category = normalize_category(state.expense.category)
    return state

def simulate_benefits_node(state: AgentState):
    expense = state.expense
    simulations = []

    for card in state.cards:
        result = {
            "card_id": card.card_id,
            "card_name": card.card_name,
            "expected_return": 0,
            "type": card.card_type,
            "details": ""
        }

        # Cashback logic
        if card.card_type == "cashback":
            rule = card.cashback_rules.get(expense.category)

            if rule:
                cashback = (expense.amount * rule.percentage) / 100

                # TODO: cap handling (next step)
                result["expected_return"] = round(cashback, 2)
                result["details"] = f"{rule.percentage}% cashback"
                result["reason"] = f"This card offers {rule.percentage}% cashback on {expense.category} purchases"

        simulations.append(result)

    state.simulations = simulations
    return state



def decide_best_card_node(state: AgentState):
    """
    Decide which card to recommend based on the simulation results
    """
    if not state.simulations:
        state.recommendation = {
            'card': 'No card',
            'expected_return': 0,
            'reason': 'No suitable card found for this expense.'
        }
        return state
    
    # Find the card with the highest return
    best_card = max(state.simulations, key=lambda x: x['expected_return'])
    
    state.recommendation = {
        'card': best_card.get('card_name', 'a credit card'),
        'expected_return': best_card.get('expected_return', 0),
        'reason': best_card.get('reason', f"This card offers the best return for this purchase")
    }
    
    return state


def format_recommendation_node(state: AgentState):
    """
    Format the recommendation into a user-friendly message using LLM
    """
    if not state.recommendation:
        state.formatted_recommendation = "No recommendation available."
        return state
    
    # Safely get recommendation details with defaults
    recommendation = state.recommendation
    card_name = recommendation.get('card', 'a credit card')
    expected_return = recommendation.get('expected_return', 0)
    reason = recommendation.get('reason', 'No specific reason provided')
    
    # If we have the raw expense, include it for better context
    expense_details = ""
    if hasattr(state, 'expense') and state.expense:
        expense = state.expense
        expense_details = f" for {expense.merchant} (₹{expense.amount:.2f})"
    
    llm = get_llm()
    
    try:
        # Get the response from the LLM
        response = llm.invoke(
            FORMAT_RECOMMENDATION_PROMPT.format(
                card=card_name,
                expected_return=expected_return,
                reason=reason,
                expense_details=expense_details
            )
        )
        
        # Extract the content safely
        if hasattr(response, 'content'):
            state.formatted_recommendation = response.content
        else:
            # Fallback to a simple formatted message if LLM call fails
            state.formatted_recommendation = (
                f"I recommend using your {card_name} card{expense_details}. "
                f"You can expect a return of {expected_return:.1f}% because {reason}"
            )
            
    except Exception as e:
        print(f"Error formatting recommendation: {e}")
        # Fallback to a simple formatted message
        state.formatted_recommendation = (
            f"I recommend using your {card_name} card{expense_details}. "
            f"You can expect a return of {expected_return:.1f}% because {reason}"
        )
    
    return state


def ingest_card_node(state, card_description: str):
    """
    Node to ingest a new card from raw text description using LLM
    """
    llm = get_llm()
    # LLM call
    response = llm.invoke(
        CARD_INGEST_PROMPT.format_messages(description=card_description)
    )

    # Parse JSON
    try:
        data = json.loads(response.content)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON from LLM: {e}\n{response.content}")

    # Parse cashback rules
    cashback_rules = {}
    for rule in data.get("cashback_rules", []):
        cashback_rules[rule["category"]] = CashbackRule(
            category=rule["category"],
            percentage=rule["percentage"],
            monthly_cap=rule.get("monthly_cap")
        )

    # Parse reward rules
    reward_rules = {}
    for rule in data.get("reward_rules", []):
        reward_rules[rule["category"]] = RewardRule(
            category=rule["category"],
            points_per_unit=rule["points_per_unit"],
            unit_amount=rule["unit_amount"],
            monthly_cap=rule.get("monthly_cap")
        )

    # Create CreditCard object
    new_card = CreditCard(
        card_id=data.get("card_name", "unknown").lower().replace(" ", "_"),
        card_name=data["card_name"],
        card_type=data["card_type"],
        cashback_rules=cashback_rules,
        reward_rules=reward_rules
    )

    # Append to state
    if not hasattr(state, "cards"):
        state.cards = []

    state.cards.append(new_card)

    return state

def router_node(state: AgentState):
    """
    Checks the user input. If message starts with /add_card, trigger card ingestion.
    Otherwise, continue with normal expense workflow.
    """
    if state.raw_message.strip().lower().startswith("/add_card"):
        # Extract the card description (everything after the command)
        state.card_description = state.raw_message[len("/add_card"):].strip()
        state.next_flow = "ingest_card"
    else:
        state.next_flow = "llm_parse_expense"
    return state


# -------- Graph -------- #

def build_workflow():
    graph = StateGraph(AgentState)

    graph.add_node("llm_parse_expense", llm_parse_expense_node)
    graph.add_node("input_expense", input_expense_node)
    graph.add_node("load_cards", load_cards_node)
    graph.add_node("load_memory", load_memory_node)
    graph.add_node("normalize_expense", normalize_expense_node)
    graph.add_node("simulate", simulate_benefits_node)
    graph.add_node("decide", decide_best_card_node)
    graph.add_node("format_recommendation", format_recommendation_node)
    graph.add_node("ingest_card", ingest_card_node)
    graph.add_node("router", router_node)

    # Entry point
    graph.set_entry_point("router")

    # Define conditional edges
    graph.add_conditional_edges(
        "router",
        lambda state: "llm_parse_expense" if state.next_flow == "llm_parse_expense" else "ingest_card"
    )
    
    # Normal expense workflow
    graph.add_edge("llm_parse_expense", "input_expense")
    graph.add_edge("input_expense", "load_cards")
    graph.add_edge("load_cards", "load_memory")
    graph.add_edge("load_memory", "normalize_expense")
    graph.add_edge("normalize_expense", "simulate")
    graph.add_edge("simulate", "decide")
    graph.add_edge("decide", "format_recommendation")
    graph.add_edge("format_recommendation", END)
    
    # Card ingestion workflow
    graph.add_edge("ingest_card", END)

    return graph.compile()
