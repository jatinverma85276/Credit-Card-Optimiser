# Add Card API Flow Diagram

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     POST /add_card                              │
│  { bank_name, card_name, user_id }                             │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 1: Web Search (Tavily API)                               │
│  ─────────────────────────────────────────────────────────────  │
│  Query: "{bank_name} {card_name} credit card features          │
│          benefits rewards India"                                │
│                                                                  │
│  Tool: search_product_price()                                   │
│  Returns: Raw text with card information from web               │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 2: LLM Parsing (GPT-4o-mini)                             │
│  ─────────────────────────────────────────────────────────────  │
│  Input: Search results text                                     │
│  Process: Structured output extraction                          │
│  Schema: CreditCard (Pydantic model)                           │
│                                                                  │
│  Extracts:                                                      │
│  • Card name, issuer, type                                     │
│  • Annual fee, waiver conditions                               │
│  • Reward rules (categories, multipliers, caps)               │
│  • Milestone benefits                                          │
│  • Eligibility criteria                                        │
│  • Key benefits, exclusions                                    │
│                                                                  │
│  Validation: extracted_from_user flag                          │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 3: Database Storage                                       │
│  ─────────────────────────────────────────────────────────────  │
│  Function: add_card(db, card_data, user_id)                    │
│  Table: credit_cards                                            │
│                                                                  │
│  Stores:                                                        │
│  • Basic fields (card_name, issuer, annual_fee, etc.)         │
│  • JSON fields (reward_rules, milestone_benefits, etc.)       │
│  • User association (user_id)                                  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  Response                                                       │
│  ─────────────────────────────────────────────────────────────  │
│  {                                                              │
│    "success": true,                                            │
│    "message": "Successfully added {card_name}...",            │
│    "card_details": { ... }                                     │
│  }                                                              │
└─────────────────────────────────────────────────────────────────┘
```

## Error Handling Flow

```
POST /add_card
     │
     ├─► Web Search Fails (404)
     │   └─► "Could not find details for {bank} {card}"
     │
     ├─► Parsing Fails (422)
     │   └─► "Could not extract valid card details"
     │       (extracted_from_user = false)
     │
     ├─► Database Error (500)
     │   └─► "Error adding card: {error}"
     │
     └─► Success (200)
         └─► Return card details
```

## Data Flow Example

### Input
```json
{
  "bank_name": "HDFC",
  "card_name": "Regalia Gold",
  "user_id": "user_123"
}
```

### Web Search Query
```
"HDFC Regalia Gold credit card features benefits rewards India"
```

### Search Results (Sample)
```
HDFC Regalia Gold Credit Card offers 4 reward points per Rs. 150 spent.
Annual fee: Rs. 2,500 (waived on spending Rs. 3 lakhs annually).
Welcome bonus: 5,000 bonus points on first transaction.
Rewards: 5X on dining, 2X on travel bookings...
```

### Parsed Structure (CreditCard Schema)
```python
CreditCard(
    extracted_from_user=True,
    card_name="HDFC Regalia Gold Credit Card",
    issuer="HDFC Bank",
    card_type="Premium",
    annual_fee="Rs. 2,500",
    fee_waiver_condition="Spend Rs. 3 lakhs annually",
    welcome_bonus="5,000 bonus points on first transaction",
    reward_program_name="HDFC Rewards",
    reward_rules=[
        RewardRule(
            category="Dining",
            multiplier="5X",
            merchants=["All restaurants"],
            cap="15,000 points per month",
            period="Month"
        ),
        RewardRule(
            category="Travel",
            multiplier="2X",
            merchants=["All travel bookings"],
            cap=None,
            period=None
        )
    ],
    key_benefits=[
        "Complimentary airport lounge access",
        "Fuel surcharge waiver"
    ],
    excluded_categories=["EMI transactions"]
)
```

### Database Record
```sql
INSERT INTO credit_cards (
    user_id,
    card_name,
    issuer,
    card_type,
    annual_fee,
    fee_waiver_condition,
    welcome_bonus,
    reward_program_name,
    reward_rules,
    key_benefits,
    excluded_categories
) VALUES (
    'user_123',
    'HDFC Regalia Gold Credit Card',
    'HDFC Bank',
    'Premium',
    'Rs. 2,500',
    'Spend Rs. 3 lakhs annually',
    '5,000 bonus points on first transaction',
    'HDFC Rewards',
    '[{"category": "Dining", "multiplier": "5X", ...}]',
    '["Complimentary airport lounge access", ...]',
    '["EMI transactions"]'
);
```

### API Response
```json
{
  "success": true,
  "message": "Successfully added HDFC Regalia Gold Credit Card to your portfolio",
  "card_details": {
    "id": 42,
    "card_name": "HDFC Regalia Gold Credit Card",
    "issuer": "HDFC Bank",
    "card_type": "Premium",
    "annual_fee": "Rs. 2,500",
    "reward_program_name": "HDFC Rewards",
    "reward_rules": [...],
    "key_benefits": [...]
  }
}
```

## Integration Points

### 1. Reuses Existing Components
- `app/tools/web_search.py` - Web search functionality
- `app/graph/nodes.py` - LLM instance and parsing logic
- `app/db/card_repository.py` - Database operations
- `app/schemas/credit_card.py` - Data models

### 2. Complements Chat Interface
- Chat: `/add_card [paste full details]` - Manual entry
- API: `POST /add_card` - Automatic search

### 3. Same Validation Rules
- Both use `extracted_from_user` flag
- Both use same card parser prompt
- Both store in same database table

## Performance Considerations

1. **Web Search**: ~2-3 seconds (Tavily API call)
2. **LLM Parsing**: ~1-2 seconds (GPT-4o-mini structured output)
3. **Database Insert**: <100ms
4. **Total**: ~3-5 seconds per card

## Security Notes

- User authentication should be added (currently accepts any user_id)
- Rate limiting recommended for web search API
- Input validation on bank_name and card_name
- Consider caching search results for popular cards
