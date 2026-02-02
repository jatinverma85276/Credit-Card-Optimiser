# app/graph/nodes.py

from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage
from langchain_core.messages import SystemMessage
from app.db.database import SessionLocal
from app.graph.schemas import CreditCard
from app.graph.state import GraphState
from dotenv import load_dotenv
from pprint import pprint

from app.db.card_repository import add_card

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)

FINANCE_KEYWORDS = {
    "expense", "expenses",
    "card", "cards",
    "category", "categories",
    "reward", "rewards",
    "cashback"
}

# -------------------------
# Router Node
# -------------------------
def router_node(state: GraphState) -> GraphState:
    last_message = state["messages"][-1].content.lower()
    # print(last_message, "Last Message")
    route = "general"
    for keyword in FINANCE_KEYWORDS:
        if keyword in last_message:
            route = "finance"
            break

    return {
        **state,
        "route": route
    }


# -------------------------
# Finance Router Node
# -------------------------
def finance_router_node(state: GraphState) -> GraphState:
    last_message = state["messages"][-1].content.strip().lower()

    if last_message.startswith("/add_card"):
        finance_route = "add_card"
    else:
        finance_route = "expense"

    return {
        **state,
        "finance_route": finance_route
    }



# # -------------------------
# # Finance Agent
# # -------------------------
# FINANCE_SYSTEM_PROMPT = """
# You are a finance assistant.
# Answer only about expenses, cards, rewards, cashback, and categories.
# Be precise and helpful.
# """

# def finance_llm_node(state: GraphState) -> GraphState:
#     messages = [
#         SystemMessage(content=FINANCE_SYSTEM_PROMPT),
#         *state["messages"]
#     ]

#     response = llm.invoke(messages)
    print(state, "Statee finance")
#     return {
#         **state,
#         "messages": state["messages"] + [response]
#     }


# -------------------------
# General Agent
# -------------------------
GENERAL_SYSTEM_PROMPT = """
You are a general assistant.
Answer normally and clearly.
"""

def general_llm_node(state: GraphState) -> GraphState:
    messages = [
        SystemMessage(content=GENERAL_SYSTEM_PROMPT),
        *state["messages"]
    ]
    # print(state, "Statee general")
    response = llm.invoke(messages)

    return {
        **state,
        "messages": state["messages"] + [response]
    }



# -------------------------
# Add Card Agent
# -------------------------
ADD_CARD_SYSTEM_PROMPT = """
You are a finance assistant.
Add a new credit/debit card based on user input.
Ask for missing details if required.
"""

def add_card_node(state: GraphState) -> GraphState:
    messages = [
        SystemMessage(content=ADD_CARD_SYSTEM_PROMPT),
        *state["messages"]
    ]
    # print(state, "Statee add card")
    response = llm.invoke(messages)

    return {
        **state,
        "messages": state["messages"] + [response]
    }



# -------------------------
# Expense Decision Agent
# -------------------------
EXPENSE_SYSTEM_PROMPT = """
You are a finance assistant.
Help the user decide which card to use for an expense.
Consider rewards, cashback, and categories.
"""

def expense_decision_node(state: GraphState) -> GraphState:
    messages = [
        SystemMessage(content=EXPENSE_SYSTEM_PROMPT),
        *state["messages"]
    ]
    # print(state, "Statee expense")
    response = llm.invoke(messages)

    return {
        **state,
        "messages": state["messages"] + [response]
    }



# -------------------------
#   Card Parser Agent
# -------------------------
CARD_EXTRACTION_PROMPT = """
You are a specialized Credit Card Data Analyst. Your job is to extract highly detailed, accurate structured data from credit card terms.

### INSTRUCTIONS:
1. **Analyze Footnotes:** Critical data (like spend caps, specific exclusions, and split categories) is often hidden in footnotes (e.g., "1", "2"). You MUST integrate this data into the main fields.
2. **Split Reward Buckets:** If a single category (like "10X Rewards") has different capping rules for different merchant groups (e.g., Group A is capped at 500, Group B is capped at 500), create **separate** `RewardRule` entries for each group.
3. **Capture Eligibility:** Extract income, age, and location constraints into the `eligibility_criteria` section.
4. **Milestones:** If the text says "Spend X to get Y", map this to `milestone_benefits`, not just `key_benefits`.
5. **Exclusions:** Be specific. If EMI is excluded only at "Point of Sale" but allowed elsewhere, mention that specific nuance.

### OUTPUT FORMAT:
Return strictly valid JSON matching the provided schema. Use `null` for missing fields. 
"""

def card_parser_node(state: GraphState) -> GraphState:
    raw_text = state["messages"][-1].content.replace("/add_card", "").strip()

    structured_llm = llm.with_structured_output(CreditCard)

    card_data: CreditCard = structured_llm.invoke([
        SystemMessage(content=ADD_CARD_SYSTEM_PROMPT),
        raw_text
    ])
    
    parsed_card = card_data  # JSON string or parsed dict
    # print("\n--- Parsed Card Data ---")
    # pprint(parsed_card.dict() if hasattr(parsed_card, "dict") else parsed_card)
    # print("------------------------\n")

    return {
        **state,
        "parsed_card": parsed_card,
        "messages": state["messages"] + [
            AIMessage(content="Card details extracted successfully.")
        ]
    }



# -------------------------
# Add Card Agent
# -------------------------
def add_card_node(state: GraphState) -> GraphState:
    card_data = state["parsed_card"]

    if not card_data:
        raise ValueError("No parsed card data found")

    if isinstance(card_data, str):
        card_data = json.loads(card_data)

    db = SessionLocal()
    try:
        add_card(db, card_data)
    finally:
        db.close()

    if hasattr(card_data, "dict"):
        card_dict = card_data.dict()
    else:
        card_dict = card_data
    return {
        **state,
        "messages": state["messages"] + [
            AIMessage(content=f"✅ {card_dict['card_name']} added successfully to your cards database.")
        ]
    }