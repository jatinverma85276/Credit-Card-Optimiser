# app/graph/nodes.py

from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
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
from langchain_core.runnables import RunnableConfig
from app.services.memory_service import save_transaction_memory
from app.utils.CONSTANTS import FINANCE_KEYWORDS
from app.tools.web_search import search_product_price, extract_price_from_search
load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
# llm = ChatGoogleGenerativeAI(
#     model="gemini-2.0-flash",  # Add 'models/' prefix
#     temperature=0.2,
# )

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
# Supreme Manage Request Node (Pure AI-Driven Router)
# -------------------------
MANAGE_REQUEST_SYSTEM_PROMPT = """
You are the Supreme Router for a Credit Card Optimization System. You have deep understanding of the entire project architecture and user intent.

## YOUR ROLE
You analyze user requests and intelligently route them to the appropriate specialized flow. You understand context, nuance, and user intent beyond simple pattern matching.

## PROJECT ARCHITECTURE KNOWLEDGE

### Flow 1: ADD_CARD_FLOW
**Purpose**: Register new credit cards into the user's portfolio
**Capabilities**:
- Parses credit card details from unstructured text (terms & conditions, marketing materials, etc.)
- Extracts: card name, issuer, fees, reward rules, benefits, eligibility criteria
- Stores structured card data in database
- Handles commands like /add_card or natural language requests

**Route here when**:
- User wants to add/register/save a new credit card
- User provides credit card details, terms, or specifications
- User mentions getting a new card and wants to track it
- User pastes card information or terms & conditions
- User uses /add_card command

**Examples**:
- "/add_card HDFC Regalia Gold Card with 5x rewards..."
- "I just got a new Amex card, can you save it?"
- "Add this card: SBI Cashback Card offers 5% on online..."
- "Register my new credit card details"

### Flow 2: RECOMMENDATION_FLOW
**Purpose**: Analyze transactions and recommend optimal credit card
**Capabilities**:
- Parses transaction details (merchant, amount, category)
- Fetches all user's registered cards
- Calculates reward points/cashback for each card
- Compares cards based on reward multipliers
- Retrieves past transaction history for context
- Provides intelligent recommendations with reasoning

**Route here when**:
- User describes a purchase/transaction/expense
- User asks which card to use for a specific merchant or category
- User wants to compare cards for a transaction
- User mentions spending money somewhere
- User asks about maximizing rewards/cashback/points
- User wants card recommendations for upcoming purchases

**Examples**:
- "I'm spending 5000 rupees on Amazon, which card should I use?"
- "Best card for groceries at BigBasket?"
- "Compare my cards for this Swiggy order"
- "Which card gives most rewards for travel booking?"
- "I'm buying electronics worth 50k, recommend a card"

### Flow 3: GENERAL_FLOW
**Purpose**: Handle general conversation and non-transactional queries
**Capabilities**:
- General conversation and chitchat
- Financial education and advice
- Questions about credit cards in general (not specific recommendations)
- Non-finance topics
- System help and guidance

**Route here when**:
- User asks general questions about credit cards, credit scores, finance
- User wants to chat or have casual conversation
- User asks about topics outside credit card optimization
- User needs help understanding how the system works
- User asks educational questions without specific transaction context

**Examples**:
- "What's a good credit score?"
- "How do credit card rewards work?"
- "Tell me about your features"
- "What's the weather today?"
- "How are you?"
- "Explain cashback vs reward points"

## ROUTING DECISION PROCESS

1. **Understand Intent**: What is the user truly trying to accomplish?
2. **Identify Context**: Is there transaction data? Card details? Or just a question?
3. **Match to Flow**: Which specialized flow best serves this intent?
4. **Decide Confidently**: Choose the single best flow

## CRITICAL RULES

- **Be Intelligent**: Don't rely on keywords. Understand the semantic meaning and user intent.
- **Consider Context**: Look at the full message, not just individual words.
- **Think Holistically**: What would best serve the user's actual need?
- **One Flow Only**: Return exactly one flow decision.
- **No Ambiguity**: Even if unclear, make your best intelligent decision.

## OUTPUT FORMAT

Return ONLY one of these three values (nothing else):
- add_card_flow
- recommendation_flow
- general_flow

Do not explain your reasoning. Just return the flow name.
"""

def manage_request_node(state: GraphState) -> GraphState:
    """
    Supreme AI-driven routing node that intelligently determines which flow to use.
    This node has deep understanding of the entire project and routes purely based on LLM reasoning.
    No keyword matching, no pattern matching - pure intelligence.
    """
    last_message = state["messages"][-1].content.strip()

    # Pure LLM-based intelligent classification
    classification_prompt = f"""
Analyze this user request and determine the optimal flow.

User Request: "{last_message}"

Think about:
1. What is the user trying to accomplish?
2. Does this involve adding a new card, getting a recommendation, or general conversation?
3. Which specialized flow would best serve this user's need?

Return ONLY the flow name: add_card_flow, recommendation_flow, or general_flow
"""

    response = llm.invoke([
        SystemMessage(content=MANAGE_REQUEST_SYSTEM_PROMPT),
        classification_prompt
    ])

    flow_decision = response.content.strip().lower()

    # Validate the response (ensure it's one of the valid flows)
    valid_flows = ["add_card_flow", "recommendation_flow", "general_flow"]
    if flow_decision not in valid_flows:
        # If LLM returns something unexpected, try to extract the flow name
        for flow in valid_flows:
            if flow in flow_decision:
                flow_decision = flow
                break
        else:
            # Ultimate fallback: ask LLM again with stricter prompt
            strict_response = llm.invoke([
                SystemMessage(content="You must return ONLY one of: add_card_flow, recommendation_flow, general_flow"),
                f"User request: {last_message}\n\nReturn only the flow name:"
            ])
            flow_decision = strict_response.content.strip().lower()

            # If still invalid, default to general_flow
            if flow_decision not in valid_flows:
                flow_decision = "general_flow"

    print(f"🎯 Supreme Router Decision: {flow_decision}")
    print(f"📝 User Request: {last_message[:100]}...")

    return {
        **state,
        "flow_decision": flow_decision
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
    # Build system prompt with memory context if available
    system_prompt = GENERAL_SYSTEM_PROMPT
    if state.get("memory_context"):
        system_prompt += f"\n\n{state['memory_context']}"
    
    messages = [
        SystemMessage(content=system_prompt),
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
def add_card_node(state: GraphState, config: RunnableConfig) -> GraphState:
    card_data = state["parsed_card"]

    if not card_data:
        raise ValueError("No parsed card data found")

    if isinstance(card_data, str):
        card_data = json.loads(card_data)

    # Get user_id from config
    user_id = config.get("configurable", {}).get("user_id", "default_user")

    db = SessionLocal()
    try:
        add_card(db, card_data, user_id)
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
You are a financial transaction extraction engine with web search capabilities.

Extract the transaction into STRICT JSON.

Rules:
- Do not guess the amount.
- Convert values like "12k", "1 lakh", "500rs" into numbers.
- Merchant must be a brand/platform if mentioned.
- Infer category only if obvious (Swiggy → food, Uber → travel).
- Return valid JSON only.
- Use null if unknown.

IMPORTANT: If the user mentions a product (like iPhone, MacBook, laptop) but doesn't provide the price,
you MUST use the search_product_price tool to find the current price before returning the transaction.

Example:
User: "I want to buy an iPhone 15"
Action: Call search_product_price("iPhone 15 price in India")
Result: Extract price from search results and set amount field
"""

def transaction_parser_node(state: GraphState, config: RunnableConfig):
    raw_text = state["messages"][-1].content.strip()

    # First, parse the transaction to see if amount is missing
    structured_llm = llm.with_structured_output(Transaction)
    parsed_txn = structured_llm.invoke([
        SystemMessage(content=TRANSACTION_PARSER_PROMPT),
        raw_text
    ])
    
    # Check if amount is missing or zero
    if parsed_txn and (parsed_txn.amount is None or parsed_txn.amount == 0):
        print(f"💰 Amount not provided. Attempting to search for price...")
        
        # Create LLM with tool binding to decide if search is needed
        llm_with_tools = llm.bind_tools([search_product_price])
        
        # Ask LLM if it should search for price
        decision_prompt = f"""
Based on this user message, should we search for the product price online?

User message: "{raw_text}"

If the message mentions a specific product (like iPhone, MacBook, laptop, etc.) that typically has a known market price, you should use the search_product_price tool.

If it's a generic expense or service (like "food", "groceries", "uber ride") without a specific product, don't search.
"""
        
        response = llm_with_tools.invoke([
            SystemMessage(content="You are a smart assistant that decides when to search for product prices."),
            decision_prompt
        ])
        
        # Check if LLM wants to use the tool
        if response.tool_calls:
            print(f"🤖 LLM decided to search for price...")
            for tool_call in response.tool_calls:
                if tool_call['name'] == 'search_product_price':
                    product_name = tool_call['args'].get('product_name', raw_text)
                    print(f"🔍 Searching for: {product_name}")
                    
                    try:
                        # Execute the search
                        search_results = search_product_price.invoke({"product_name": product_name})
                        estimated_price = extract_price_from_search(search_results, product_name)
                        
                        if estimated_price > 0:
                            print(f"✅ Found estimated price: ₹{estimated_price}")
                            parsed_txn.amount = estimated_price
                        else:
                            print(f"⚠️ Could not find price online. Using amount = 0")
                    except Exception as e:
                        print(f"⚠️ Web search failed: {e}")
        else:
            print(f"🤖 LLM decided search is not needed for this query")

    # --- 🧠 VECTOR MEMORY INJECTION (Skip in incognito mode) ---
    incognito = config.get("configurable", {}).get("incognito", False)
    
    if parsed_txn and not incognito:
        try:
            # Get the user ID
            user_id = config.get("configurable", {}).get("user_id", "default")
            # Save to Postgres Vector DB
            save_transaction_memory(
                user_id=user_id,
                merchant=parsed_txn.merchant,
                amount=parsed_txn.amount,
                category=parsed_txn.category,
                desc=state["messages"][-1].content  # Save original query as description
            )
            print(f"✅ Saved Semantic Memory: {parsed_txn.merchant}")
            
        except Exception as e:
            # CRITICAL: Do not crash the flow if DB save fails
            print(f"⚠️ Memory Save Failed: {e}")
    elif incognito:
        print(f"🕵️ Incognito mode: Transaction memory not saved")
    # ---------------------------------------

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
from app.db.card_repository import get_user_cards

def fetch_user_cards_node(state: GraphState, config: RunnableConfig) -> GraphState:
    # Get user_id from config
    user_id = config.get("configurable", {}).get("user_id", "default_user")
    
    db = SessionLocal()
    try:
        rows = get_user_cards(db, user_id)
    finally:
        db.close()

    cards = []

    for row in rows:
        try:
            # 1. Deserialize the nested JSON fields first
            reward_rules_data = row.reward_rules if row.reward_rules else []
            excluded_data = row.excluded_categories if row.excluded_categories else []
            benefits_data = row.key_benefits if row.key_benefits else []
            
            # Handle new fields if you added them (Milestones, Eligibility)
            milestones_data = row.milestone_benefits if row.milestone_benefits else []
            eligibility_data = row.eligibility_criteria if row.eligibility_criteria else None

            # 2. Reconstruct the Pydantic Object
            card = CreditCard(
                card_name=row.card_name,
                issuer=row.issuer,
                card_type=row.card_type,
                annual_fee=row.annual_fee,
                fee_waiver_condition=row.fee_waiver_condition,
                welcome_bonus=row.welcome_bonus,
                reward_program_name=row.reward_program_name,
                
                # Pass the parsed lists/dicts
                reward_rules=[RewardRule(**r) for r in reward_rules_data],
                milestone_benefits=[Milestone(**m) for m in milestones_data],
                eligibility_criteria=Eligibility(**eligibility_data) if eligibility_data else None,
                excluded_categories=excluded_data,
                key_benefits=benefits_data,
                
                liability_policy=row.liability_policy if row.liability_policy else None
            )
            
            cards.append(card)

        except Exception as e:
            print(f"Failed to parse card '{row.card_name}':", e)
            import traceback
            traceback.print_exc()

    # If no cards found, prompt user to add cards
    if len(cards) == 0:
        return {
            **state,
            "available_cards": [],
            "messages": state["messages"] + [
                AIMessage(content="You don't have any credit cards registered yet. Please add your credit cards first using the /add_card command to get personalized recommendations.\n\nExample: `/add_card HDFC Regalia Gold Card with 5x rewards on dining...`")
            ]
        }

    print(f"\n✅ Loaded {len(cards)} cards for user {user_id}")

    return {
        **state,
        "available_cards": cards,
        "messages": state["messages"] + [
            AIMessage(content=f"Fetched {len(cards)} cards from your portfolio.")
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
        
        # Handle None category
        category_lower = txn.category.lower() if txn.category else ""
        
        if category_lower in exclusions or merchant_input in exclusions:
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
# def llm_recommendation_node(state: GraphState) -> GraphState:

#     best_card = state["best_card"]
#     txn = state["parsed_transaction"]
#     breakdown = state["reward_breakdown"]

#     best_entry = next(
#         b for b in breakdown if b["card_name"] == best_card.card_name
#     )

#     prompt = f"""
#             You are a smart financial assistant.

#             Explain the credit card recommendation clearly.

#                 Transaction:
#                 - Merchant: {txn.merchant}
#                 - Amount: ₹{txn.amount}

#                 Best Card:
#                 - Card: {best_card.card_name}
#                 - Reward Multiplier: {best_entry['multiplier']}x
#                 - Estimated Points: {round(best_entry['points'],2)}

#                 Keep it:
#                 ✔ Clear
#                 ✔ Professional
#                 ✔ Helpful
#                 ✔ Not too long
#             """

#     response = llm.invoke(prompt)

#     return {
#         **state,
#         "messages": state["messages"] + [
#             response
#         ]
#     }

# -------------------------
# LLM Recommendation Agent (Fixed)
# # -------------------------
# LLM Recommendation Agent (Comparison Optimized)
# -------------------------
def llm_recommendation_node(state: GraphState) -> GraphState:

    # 1. Extract Context
    txn = state.get("parsed_transaction")
    breakdown = state.get("reward_breakdown", [])
    ltm_context = state.get("memory_context", "")
    
    # CRITICAL: Get the user's specific question
    user_query = state["messages"][-1].content

    # 2. Prepare Data String
    breakdown_text = ""
    for item in breakdown:
        breakdown_text += (
            f"- {item['card_name']}: {round(item['points'], 2)} Points "
            f"(Multiplier: {item['multiplier']}x | Category: {item['category']})\n"
        )
    if not breakdown_text:
        breakdown_text = "No cards matched for this transaction."

    # 3. The "Comparison-First" Prompt
    prompt = f"""
    You are a Credit Card Strategy Expert.

    ### LONG-TERM MEMORY (PAST CONTEXT)
    {ltm_context}  <-- ✅ INJECTED HERE (If empty, this line is blank)

    ### DATA (Calculated Rewards)
    {breakdown_text}

    ### TRANSACTION
    Merchant: {txn.merchant if txn else 'Unknown'} | Amount: ₹{txn.amount if txn else 0}

    ### USER QUESTION
    "{user_query}"

    ### STRICT RESPONSE RULES:
    1. **IF "COMPARE" IS ASKED:** - DO NOT simply list all cards.
       - Identify the SPECIFIC cards the user asked about (e.g., "IDFC" and "Flipkart").
       - Create a "Head-to-Head" comparison for ONLY those cards.
       - Example: "The Flipkart SBI earns 750 pts (7.5x), whereas IDFC Select earns only 300 pts (3x). This makes Flipkart 2.5x more rewarding."

    2. **IF "BEST CARD" IS ASKED:**
       - Announce the winner clearly.
       - Briefly list the runners-up.

    3. **Tone:**
       - Be direct. Avoid generic filler like "Based on your transaction..."
       - Start immediately with the answer.
    """

    # 4. Invoke LLM
    response = llm.invoke(prompt)

    return {
        **state,
        "messages": state["messages"] + [response]
    }

# -------------------------
# LLM Recommendation Agent (Comparison Logic Fixed)
# -------------------------
# def llm_recommendation_node(state: GraphState) -> GraphState:

#     # 1. Extract Context
#     txn = state.get("parsed_transaction")
#     breakdown = state.get("reward_breakdown", [])
#     user_query = state["messages"][-1].content.lower() # Normalize to lowercase

#     # 2. INTENT DETECTION: Check if user wants to "Compare"
#     is_comparison = "compare" in user_query or "difference" in user_query or "vs" in user_query

#     # 3. FILTER DATA (If Comparison)
#     # If the user asks "Compare IDFC and Flipkart", we try to find those specific cards.
#     # Otherwise, we show all cards.
    
#     selected_cards_text = ""
    
#     if is_comparison:
#         # Simple keyword matching to find which cards to compare
#         relevant_items = []
#         for item in breakdown:
#             # Check if card name matches any word in user query (e.g., "idfc", "flipkart")
#             card_name_lower = item['card_name'].lower()
#             if any(word in card_name_lower for word in user_query.split()):
#                 relevant_items.append(item)
        
#         # If we found matches, only show those. If not, show all (fallback).
#         items_to_show = relevant_items if relevant_items else breakdown
#         header = "### TARGET CARDS FOR COMPARISON"
#     else:
#         items_to_show = breakdown
#         header = "### CALCULATED REWARDS (LEADERBOARD)"

#     # 4. Build the Data String
#     for item in items_to_show:
#         selected_cards_text += (
#             f"- {item['card_name']}: {round(item['points'], 2)} Points "
#             f"(Multiplier: {item['multiplier']}x | Category: {item['category']})\n"
#         )
    
#     if not selected_cards_text:
#         selected_cards_text = "No cards matched for this transaction."

#     # 5. DYNAMIC PROMPT SELECTION
#     if is_comparison:
#         # --- MODE A: COMPARISON ---
#         prompt = f"""
#         You are a Credit Card Analyst. The user wants a HEAD-TO-HEAD comparison.

#         {header}
#         {selected_cards_text}

#         ### USER QUESTION
#         "{state["messages"][-1].content}"

#         ### INSTRUCTION
#         1. **IGNORE THE 'WINNER'.** Do not just say who won.
#         2. **COMPARE:** Explain the difference in points/multiplier between the specific cards listed above.
#         3. **VERDICT:** Conclude with "Card A is X times better than Card B for this purchase."
#         """
#     else:
#         # --- MODE B: RECOMMENDATION (Standard) ---
#         prompt = f"""
#         You are a Credit Card Expert. Recommend the best card.

#         {header}
#         {selected_cards_text}

#         ### TRANSACTION
#         Merchant: {txn.merchant if txn else 'Unknown'} | Amount: ₹{txn.amount if txn else 0}

#         ### INSTRUCTION
#         1. Announce the Winner clearly.
#         2. List runners-up briefly.
#         3. Explain WHY the winner is best (e.g., "7.5x reward rate").
#         """

#     # 6. Invoke LLM
#     print(f"DEBUG: Comparison Mode = {is_comparison}")
#     response = llm.invoke(prompt)

#     return {
#         **state,
#         "messages": state["messages"] + [response]
#     }