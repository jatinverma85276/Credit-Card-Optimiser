# Add Card API Documentation

## Overview

The `/add_card` endpoint allows you to add credit cards to a user's portfolio by simply providing the bank name and card name. The system will automatically:

1. Search for card details online using web search
2. Extract and parse structured card information (rewards, fees, benefits, etc.)
3. Save the card to the database with all details

## Endpoint

```
POST /add_card
```

## Request Body

```json
{
  "bank_name": "string",
  "card_name": "string", 
  "user_id": "string"
}
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `bank_name` | string | Yes | Name of the bank/issuer (e.g., "HDFC", "ICICI", "American Express") |
| `card_name` | string | Yes | Name of the credit card (e.g., "Regalia Gold", "Amazon Pay", "Platinum Travel") |
| `user_id` | string | Yes | User ID to associate the card with |

## Response

### Success Response (200 OK)

```json
{
  "success": true,
  "message": "Successfully added HDFC Regalia Gold Card to your portfolio",
  "card_details": {
    "id": 1,
    "card_name": "HDFC Regalia Gold Credit Card",
    "issuer": "HDFC Bank",
    "card_type": "Premium",
    "annual_fee": "Rs. 2,500",
    "reward_program_name": "HDFC Rewards",
    "reward_rules": [
      {
        "category": "Dining",
        "multiplier": "5X",
        "merchants": ["All restaurants"],
        "cap": "15,000 points per month"
      }
    ],
    "key_benefits": [
      "Complimentary airport lounge access",
      "Fuel surcharge waiver"
    ]
  }
}
```

### Error Responses

#### 404 Not Found
Card details could not be found online:

```json
{
  "detail": "Could not find details for HDFC XYZ Card. Please try with more specific card name or add details manually."
}
```

#### 422 Unprocessable Entity
Search results were too generic or incomplete:

```json
{
  "detail": "Could not extract valid card details from search results. The information found was too generic or incomplete. Please try adding the card manually with full details."
}
```

#### 500 Internal Server Error
Server error during processing:

```json
{
  "detail": "Error adding card: [error message]"
}
```

## Usage Examples

### cURL

```bash
curl -X POST "http://localhost:8000/add_card" \
  -H "Content-Type: application/json" \
  -d '{
    "bank_name": "HDFC",
    "card_name": "Regalia Gold",
    "user_id": "user_123"
  }'
```

### Python (requests)

```python
import requests

response = requests.post(
    "http://localhost:8000/add_card",
    json={
        "bank_name": "HDFC",
        "card_name": "Regalia Gold",
        "user_id": "user_123"
    }
)

if response.status_code == 200:
    result = response.json()
    print(f"Success: {result['message']}")
    print(f"Card ID: {result['card_details']['id']}")
else:
    print(f"Error: {response.json()['detail']}")
```

### JavaScript (fetch)

```javascript
fetch('http://localhost:8000/add_card', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    bank_name: 'HDFC',
    card_name: 'Regalia Gold',
    user_id: 'user_123'
  })
})
.then(response => response.json())
.then(data => {
  if (data.success) {
    console.log('Success:', data.message);
    console.log('Card Details:', data.card_details);
  }
})
.catch(error => console.error('Error:', error));
```

## How It Works

### 1. Web Search
The endpoint constructs a search query:
```
"{bank_name} {card_name} credit card features benefits rewards India"
```

Example: `"HDFC Regalia Gold credit card features benefits rewards India"`

### 2. Information Extraction
The system uses an LLM with structured output to extract:
- Card name and issuer
- Card type (Premium, Platinum, etc.)
- Annual fee and waiver conditions
- Welcome bonus
- Reward rules (categories, multipliers, caps)
- Milestone benefits
- Eligibility criteria
- Excluded categories
- Key benefits
- Liability policy

### 3. Database Storage
The parsed card details are saved to the `credit_cards` table with:
- User association (`user_id`)
- All extracted fields
- JSON fields for complex data (reward rules, milestones, etc.)

## Supported Card Examples

The endpoint works best with well-known credit cards:

- **HDFC**: Regalia Gold, Diners Club Black, Millennia
- **ICICI**: Amazon Pay, Sapphiro, Coral
- **SBI**: Cashback, SimplyCLICK, Elite
- **American Express**: Platinum Travel, Gold Card, SmartEarn
- **Axis**: Magnus, Vistara, Flipkart
- **Kotak**: 811, Royale Signature, Zen

## Tips for Best Results

1. **Use official card names**: "Regalia Gold" instead of "Regalia"
2. **Include bank name**: Helps narrow down search results
3. **Be specific**: "Amazon Pay" instead of just "Amazon"
4. **Check popular cards**: Well-known cards have better online documentation

## Integration with Existing Flow

This endpoint complements the existing `/add_card` command in the chat interface:

- **Chat command**: `/add_card [paste full card details]` - Manual entry with full T&C
- **API endpoint**: `POST /add_card` - Automatic search and extraction

Both methods use the same card parser and database storage logic.

## Testing

Run the test script to verify the endpoint:

```bash
python test_add_card_api.py
```

Make sure your server is running on port 8000 before testing.

## Notes

- The web search uses the Tavily API (configured in `app/tools/web_search.py`)
- Card details are extracted using GPT-4o-mini with structured output
- The same validation rules apply as the chat-based `/add_card` command
- Multiple users can have the same card (no unique constraint on card_name)
