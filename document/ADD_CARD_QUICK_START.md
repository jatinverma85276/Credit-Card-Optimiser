# Add Card API - Quick Start Guide

## What's New?

A new `/add_card` API endpoint that automatically fetches credit card details from the web and adds them to your database. Just provide the bank name and card name!

## Quick Example

```bash
curl -X POST "http://localhost:8000/add_card" \
  -H "Content-Type: application/json" \
  -d '{
    "bank_name": "HDFC",
    "card_name": "Regalia Gold",
    "user_id": "user_123"
  }'
```

Response:
```json
{
  "success": true,
  "message": "Successfully added HDFC Regalia Gold Credit Card to your portfolio",
  "card_details": {
    "id": 1,
    "card_name": "HDFC Regalia Gold Credit Card",
    "issuer": "HDFC Bank",
    "annual_fee": "Rs. 2,500",
    "reward_rules": [...],
    "key_benefits": [...]
  }
}
```

## How to Use

### 1. Start Your Server

```bash
# Make sure your FastAPI server is running
uvicorn main:app --reload
```

### 2. Test the Endpoint

```bash
# Run the test script
python test_add_card_api.py
```

### 3. Add Your Cards

```python
import requests

# Add a card
response = requests.post(
    "http://localhost:8000/add_card",
    json={
        "bank_name": "ICICI",
        "card_name": "Amazon Pay",
        "user_id": "your_user_id"
    }
)

print(response.json())
```

## What Happens Behind the Scenes?

1. **Web Search**: Searches for "{bank_name} {card_name} credit card features benefits rewards India"
2. **AI Parsing**: Extracts structured data (fees, rewards, benefits, etc.)
3. **Database Save**: Stores the card in your `credit_cards` table

## Supported Cards

Works best with popular Indian credit cards:

- HDFC: Regalia Gold, Diners Club Black, Millennia
- ICICI: Amazon Pay, Sapphiro, Coral
- SBI: Cashback, SimplyCLICK, Elite
- Axis: Magnus, Vistara, Flipkart
- American Express: Platinum Travel, Gold Card

## Error Handling

### Card Not Found
```json
{
  "detail": "Could not find details for XYZ Card. Please try with more specific card name."
}
```
**Solution**: Use the official card name or add manually via chat

### Incomplete Information
```json
{
  "detail": "Could not extract valid card details from search results."
}
```
**Solution**: The search results were too generic. Try a more specific card name.

## Integration with Chat

You can still use the chat interface for manual entry:

```
/add_card HDFC Regalia Gold Card
Annual Fee: Rs. 2,500
Rewards: 5X on dining...
[paste full details]
```

The API is perfect when you just know the card name and want automatic extraction!

## Files Modified/Created

### Modified
- `main.py` - Added `/add_card` endpoint

### Created
- `test_add_card_api.py` - Test script
- `ADD_CARD_API_DOCUMENTATION.md` - Full API docs
- `ADD_CARD_FLOW_DIAGRAM.md` - Architecture diagram
- `ADD_CARD_QUICK_START.md` - This file

## Next Steps

1. Test with your favorite cards
2. Integrate into your frontend
3. Add authentication/authorization
4. Consider caching for popular cards

## Need Help?

- Check `ADD_CARD_API_DOCUMENTATION.md` for detailed API reference
- Check `ADD_CARD_FLOW_DIAGRAM.md` for architecture details
- Run `python test_add_card_api.py` to verify setup

## Example Frontend Integration

```javascript
// React example
async function addCard(bankName, cardName, userId) {
  try {
    const response = await fetch('http://localhost:8000/add_card', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        bank_name: bankName,
        card_name: cardName,
        user_id: userId
      })
    });
    
    const data = await response.json();
    
    if (data.success) {
      console.log('Card added:', data.card_details);
      return data.card_details;
    } else {
      console.error('Failed to add card:', data.detail);
      return null;
    }
  } catch (error) {
    console.error('Error:', error);
    return null;
  }
}

// Usage
addCard('HDFC', 'Regalia Gold', 'user_123');
```

Happy coding! 🎉
