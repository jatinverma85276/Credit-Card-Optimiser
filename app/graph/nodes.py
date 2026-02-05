# app/graph/nodes.py

from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage
from langchain_core.messages import SystemMessage
from app.schemas.transaction import Transaction
from app.db.database import SessionLocal
from app.schemas.credit_card import CreditCard
from app.graph.state import GraphState
from dotenv import load_dotenv
from pprint import pprint
import sqlite3
import json
from app.db.card_repository import add_card
from app.utils.CONSTANTS import FINANCE_KEYWORDS

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)

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
You are a STRICT Financial Data Extractor. Your goal is to map unstructured text to a structured schema with 100% fidelity to the source text.

### CORE PHILOSOPHY:
1. **NO INFERENCE:** If the user says "5% on travel", extract exactly that. Do NOT infer "Foreign Transaction Fee Waiver" unless explicitly stated.
2. **NO AUTOFILL:** Do not fill in generic data (like "18 years old" or "Indian Resident") unless the text explicitly mentions these criteria.
3. **NO GUESSING:** If a field (like `annual_fee`) is missing from the text, return `null`. Do not guess based on similar cards.

### DATA HANDLING RULES:
1. **Analyze Footnotes:** Critical data (caps, specific exclusions) is often hidden in footnotes (e.g., "1", "2"). You MUST integrate this data into the main fields.
2. **Split Reward Buckets:** If a single category (like "10X Rewards") has different caps for different merchant groups (e.g., "Group A capped at 500, Group B capped at 500"), create **separate** `RewardRule` entries.
3. **Capture Eligibility:** Extract income, age, and location constraints into `eligibility_criteria` ONLY if explicitly mentioned.
4. **Milestones:** Map "Spend X to get Y" logic to `milestone_benefits`.
5. **Exclusions:** Be specific. If EMI is excluded only at "Point of Sale", record that nuance.

### VALIDATION & FAILURE HANDLING:
- **`extracted_from_user` Flag:** - Set to `true` IF the text contains specific, identifiable credit card terms (e.g., specific reward rates, fee amounts, or unique benefit names).
  - Set to `false` IF the input is vague, generic, or lacks sufficient detail to identify a specific financial product (e.g., "I want a travel card" or "Show me Amex cards").

### OUTPUT FORMAT:
Return strictly valid JSON matching the provided schema. 
"""

def card_parser_node(state: GraphState) -> GraphState:
    raw_text = state["messages"][-1].content.replace("/add_card", "").strip()

    # 2. CRITICAL CHECK: If text is empty, ask user for details
    if not raw_text:
        return {
            **state,
            "parsed_card": None,
            "messages": state["messages"] + [
                AIMessage(content="Please paste the credit card details or terms and conditions after the command. \nExample: `/add_card American Express SmartEarn terms...`")
            ]
        }

    # 3. Proceed only if text exists
    # print("Raw text:", raw_text)

    structured_llm = llm.with_structured_output(CreditCard)

    # print("Structured LLM:", structured_llm)

    card_data: CreditCard = structured_llm.invoke([
        SystemMessage(content=ADD_CARD_SYSTEM_PROMPT),
        raw_text
    ])
    
    if not card_data.extracted_from_user:
         return {
            **state,
            "parsed_card": None,
            "messages": state["messages"] + [
                AIMessage(content="I couldn't find any valid credit card details in your message. Please provide the full terms or features.")
            ]
        }
    parsed_card = card_data  # JSON string or parsed dict
    # print("\n--- Parsed Card Data ---")
    # print(parsed_card, "Parsed Card")
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


# -------------------------
# Transaction Parser Agent
# -------------------------
TRANSACTION_PARSER_PROMPT = """
You are a financial transaction extraction engine.

Extract the transaction into STRICT JSON.

Rules:
- Do not guess the amount.
- Convert values like "12k", "1 lakh", "500rs" into numbers.
- Merchant must be a brand/platform if mentioned.
- Infer category only if obvious (Swiggy → food, Uber → travel).
- Return valid JSON only.
- Use null if unknown.
"""

def transaction_parser_node(state: GraphState) -> GraphState:

    raw_text = state["messages"][-1].content.strip()

    structured_llm = llm.with_structured_output(Transaction)

    parsed_txn: Transaction = structured_llm.invoke([
        SystemMessage(content=TRANSACTION_PARSER_PROMPT),
        raw_text
    ])
    # print(state, "State")
    # print(parsed_txn.model_dump(), "Parsed Transaction")

    return {
        **state,
        "parsed_transaction": parsed_txn,
        "messages": state["messages"] + [
            AIMessage(content="Transaction parsed successfully.")
        ]
    }



# -------------------------
# Fetch User Cards Agent
# -------------------------
from app.schemas.credit_card import CreditCard, RewardRule, Milestone, Eligibility  # Import your Pydantic models

def fetch_user_cards_node(state: GraphState) -> GraphState:
    conn = sqlite3.connect("cards.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM credit_cards")
    rows = cursor.fetchall()
    
    # DEBUG: Print actual column names to confirm schema
    # if len(rows) > 0:
    #     print("Available Columns:", rows[0].keys())

    cards = []

    for row in rows:
        try:
            # 1. Deserialize the nested JSON fields first
            # We use json.loads() because raw SQLite returns these as strings
            reward_rules_data = json.loads(row["reward_rules"]) if row["reward_rules"] else []
            excluded_data = json.loads(row["excluded_categories"]) if row["excluded_categories"] else []
            benefits_data = json.loads(row["key_benefits"]) if row["key_benefits"] else []
            
            # Handle new fields if you added them (Milestones, Eligibility)
            milestones_data = json.loads(row["milestone_benefits"]) if "milestone_benefits" in row.keys() and row["milestone_benefits"] else []
            eligibility_data = json.loads(row["eligibility_criteria"]) if "eligibility_criteria" in row.keys() and row["eligibility_criteria"] else None

            # 2. Reconstruct the Pydantic Object
            card = CreditCard(
                card_name=row["card_name"],
                issuer=row["issuer"],
                card_type=row["card_type"],
                annual_fee=row["annual_fee"],
                fee_waiver_condition=row["fee_waiver_condition"],
                welcome_bonus=row["welcome_bonus"],
                reward_program_name=row["reward_program_name"], # Note: we renamed this column earlier
                
                # Pass the parsed lists/dicts
                reward_rules=[RewardRule(**r) for r in reward_rules_data],
                milestone_benefits=[Milestone(**m) for m in milestones_data],
                eligibility_criteria=Eligibility(**eligibility_data) if eligibility_data else None,
                excluded_categories=excluded_data,
                key_benefits=benefits_data,
                
                liability_policy=row["liability_policy"] if "liability_policy" in row.keys() else None
            )
            
            cards.append(card)

        except Exception as e:
            print(f"Failed to parse card '{row['card_name']}':", e)
            import traceback
            traceback.print_exc() # Helps see exactly which field failed

    conn.close()

    # print(f"\n✅ Loaded {cards} cards")

    return {
        **state,
        "available_cards": cards,
        "messages": state["messages"] + [
            AIMessage(content=f"Fetched {len(cards)} cards.")
        ]
    }



# -------------------------
# Reward Calculation Agent
# -------------------------
import re
from langchain_core.messages import AIMessage

def reward_calculation_node(state: GraphState) -> GraphState:
    txn = state.get("parsed_transaction")
    cards = state.get("available_cards", [])

    if not txn:
        raise ValueError("Transaction missing in state")
    
    if not cards:
        return {**state, "messages": state["messages"] + [AIMessage(content="No cards found.")]}

    # Normalize inputs
    merchant_input = txn.merchant.lower().strip()
    amount = float(txn.amount)

    best_card = None
    best_points = -1
    breakdown = []

    for card in cards:
        # --- 1. EXCLUSIONS ---
        exclusions = [e.lower() for e in card.excluded_categories] if card.excluded_categories else []
        if txn.category.lower() in exclusions or merchant_input in exclusions:
            breakdown.append({
                "card_name": card.card_name,
                "points": 0,
                "category": "Excluded",
                "reason": "Matches exclusion"
            })
            continue

        # --- 2. FIND BEST MATCHING RULE ---
        applied_multiplier = 1.0
        applied_category = "Base Reward"
        
        # Sort: Specific merchants first, "All" last
        sorted_rules = sorted(
            card.reward_rules, 
            key=lambda r: "all" in [m.lower() for m in r.merchants]
        )

        for rule in sorted_rules:
            rule_merchants = [m.lower() for m in rule.merchants]
            
            # --- MATCHING LOGIC (The Fix) ---
            match_found = False
            
            # 1. Generic Match
            if "all" in rule_merchants:
                match_found = True
            
            # 2. Specific Match (Exact or Substring)
            # Check if any DB merchant (e.g. 'nykaa') is inside User Input (e.g. 'nykaa man')
            # OR if User Input (e.g. 'uber') is inside DB merchant (e.g. 'uber eats')
            else:
                for rm in rule_merchants:
                    if rm in merchant_input or merchant_input in rm:
                        match_found = True
                        break

            if match_found:
                raw_mult = str(rule.multiplier).strip()
                
                # --- PARSING LOGIC ---
                try:
                    if "x" in raw_mult.lower():
                        applied_multiplier = float(raw_mult.lower().replace("x", "").strip())
                    elif "%" in raw_mult:
                        # Treating 1% approx equal to 1 Point for comparison
                        applied_multiplier = float(raw_mult.replace("%", "").strip())
                    else:
                        # Regex extraction for "2 travel credits..."
                        match = re.search(r"(\d+(\.\d+)?)", raw_mult)
                        applied_multiplier = float(match.group(1)) if match else 1.0

                except Exception:
                    applied_multiplier = 1.0

                applied_category = rule.category
                
                # If this was a SPECIFIC match (not "all"), we stop looking.
                # If it was "all", we keep looking in case a specific rule exists later?
                # Actually, since we sorted "All" to the bottom, if we hit "All" here, 
                # it means we already missed the specific ones. 
                # BUT: Since we are iterating *sorted* list where "All" is last, 
                # if we hit a specific match, we should break immediately.
                if "all" not in rule_merchants:
                    break 

        # --- 3. CALCULATION ---
        points = (amount / 50) * applied_multiplier

        breakdown.append({
            "card_name": card.card_name,
            "multiplier": applied_multiplier,
            "category": applied_category,
            "points": round(points, 2)
        })

        if points > best_points:
            best_points = points
            best_card = card

    if best_card:
        msg = f"Best choice: **{best_card.card_name}**.\nEarn approx **{int(best_points)} points** ({breakdown[-1]['category']})."
    else:
        msg = "No suitable card found."

    return {
        **state,
        "best_card": best_card,
        "reward_breakdown": breakdown,
        "messages": state["messages"] + [AIMessage(content=msg)]
    }




# -------------------------
# Decision Agent
# -------------------------
def decision_node(state: GraphState) -> GraphState:

    txn = state["parsed_transaction"]
    best_card = state.get("best_card")
    breakdown = state.get("reward_breakdown", [])

    # Safety check
    if not best_card:
        return {
            **state,
            "messages": state["messages"] + [
                AIMessage(content="I couldn't find a suitable card for this transaction.")
            ]
        }

    merchant = txn.merchant
    amount = txn.amount

    # Find best card points
    best_entry = next(
        (b for b in breakdown if b["card_name"] == best_card.card_name),
        None
    )

    points = round(best_entry["points"], 2)
    multiplier = best_entry["multiplier"]
    category = best_entry["category"]

    response = f"""
💳 **Best Card Recommendation**

Use **{best_card.card_name}** for this transaction at **{merchant}**.

🎯 You'll earn approximately **{points} reward points**  
⚡ Reward Rate: **{multiplier}x** ({category})

Smart choice for maximizing rewards!
"""

    return {
        **state,
        "messages": state["messages"] + [
            AIMessage(content=response)
        ]
    }




# -------------------------
# LLM Recommendation Agent
# -------------------------
def llm_recommendation_node(state: GraphState) -> GraphState:

    best_card = state["best_card"]
    txn = state["parsed_transaction"]
    breakdown = state["reward_breakdown"]

    best_entry = next(
        b for b in breakdown if b["card_name"] == best_card.card_name
    )

    prompt = f"""
            You are a smart financial assistant.

            Explain the credit card recommendation clearly.

                Transaction:
                - Merchant: {txn.merchant}
                - Amount: ₹{txn.amount}

                Best Card:
                - Card: {best_card.card_name}
                - Reward Multiplier: {best_entry['multiplier']}x
                - Estimated Points: {round(best_entry['points'],2)}

                Keep it:
                ✔ Clear
                ✔ Professional
                ✔ Helpful
                ✔ Not too long
            """

    response = llm.invoke(prompt)

    return {
        **state,
        "messages": state["messages"] + [
            response
        ]
    }
