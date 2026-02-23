# Web Search for Product Pricing

## Overview

The system now automatically searches for product prices online when users don't provide the amount. This is especially useful for expensive products like electronics where users might not know the exact price.

## How It Works

### Intelligent Price Detection with LLM

The system uses an LLM-powered decision engine to intelligently determine when to search for prices online. No hardcoded keywords - the LLM understands context and decides autonomously.

**User Input:**
```
"I want to buy an iPhone 15"
```

**System Behavior:**
1. Transaction parser attempts to extract amount from user message
2. If amount is missing (0 or null), LLM analyzes the message
3. LLM decides if the message mentions a specific product that needs price lookup
4. If yes, LLM calls the `search_product_price` tool with the product name
5. System searches Tavily API for current price in India
6. Extracts price from search results using regex patterns
7. Uses estimated price for card recommendation

**Result:**
```
💰 Amount not provided. Attempting to search for price...
🤖 LLM decided to search for price...
🔍 Searching for: iPhone 15
✅ Found estimated price: ₹79,900
```

### Smart Decision Making

The LLM intelligently decides when to search:

**Will Search:**
- "I want to buy an iPhone 15" ✅ (specific product)
- "Buying MacBook Pro M3" ✅ (specific product)
- "Samsung Galaxy S24 purchase" ✅ (specific product)

**Won't Search:**
- "I spent money on food" ❌ (generic category)
- "Uber ride to airport" ❌ (service, not product)
- "Groceries at BigBasket" ❌ (no specific product)

No hardcoded keywords needed - the LLM understands context!

## Examples

### Example 1: iPhone Purchase

**Input:**
```json
{
  "message": "I'm buying an iPhone 15 Pro",
  "user": {...}
}
```

**System Process:**
```
1. Parse transaction → amount = null
2. Detect "iPhone" keyword
3. Search: "iPhone 15 Pro price in India"
4. Extract price: ₹1,34,900
5. Calculate rewards with estimated price
```

**Response:**
```
💳 Best Card Recommendation

Use HDFC Regalia Gold Card for this transaction at Apple Store.

🎯 You'll earn approximately 2,698 reward points
⚡ Reward Rate: 5x (Electronics)

Note: Price estimated via web search: ₹1,34,900
```

### Example 2: MacBook Purchase

**Input:**
```json
{
  "message": "Which card should I use for MacBook Pro M3?",
  "user": {...}
}
```

**System Process:**
```
1. Parse transaction → amount = null
2. Detect "MacBook" keyword
3. Search: "MacBook Pro M3 price in India"
4. Extract price: ₹1,99,900
5. Calculate rewards
```

### Example 3: With Amount Provided (No Search)

**Input:**
```json
{
  "message": "I'm spending 80000 on iPhone",
  "user": {...}
}
```

**System Process:**
```
1. Parse transaction → amount = 80000
2. Amount provided, skip web search
3. Calculate rewards directly
```

## Technical Implementation

### Web Search Tool

Located in `app/tools/web_search.py`:

```python
@tool
def search_product_price(product_name: str) -> str:
    """
    Search for product price using Tavily API
    
    Args:
        product_name: Name of the product to search for
    
    Returns:
        str: Search results containing price information
    """
    query = f"{product_name} price in India"
    results = tavily_search.invoke(query)
    return combined_results
```

### LLM-Powered Decision Engine

The system uses tool binding to let the LLM decide when to search:

```python
# Bind the search tool to LLM
llm_with_tools = llm.bind_tools([search_product_price])

# LLM analyzes the message and decides
response = llm_with_tools.invoke([
    SystemMessage(content="Decide if we should search for price"),
    user_message
])

# If LLM calls the tool, execute the search
if response.tool_calls:
    search_results = search_product_price.invoke({"product_name": product_name})
    estimated_price = extract_price_from_search(search_results)
```

### Price Extraction

Uses regex patterns to extract prices:
- `₹50,000`
- `Rs. 50000`
- `INR 50000`
- `Price: ₹50000`
- `MRP: ₹50000`

Filters out unrealistic prices (< ₹100 or > ₹1 crore)

### Integration Point

In `transaction_parser_node`:
1. Parse transaction first
2. Check if amount is missing
3. Let LLM decide if search is needed
4. Execute search if LLM calls the tool
5. Extract and use estimated price

## Configuration

### No Configuration Needed!

The beauty of the LLM-powered approach is that you don't need to maintain keyword lists. The LLM understands context and makes intelligent decisions.

### Adjusting Price Filters

Edit `app/tools/web_search.py`:

```python
# Current: Between ₹100 and ₹1 crore
if 100 < price < 10000000:
    prices.append(price)

# Adjust as needed:
if 500 < price < 5000000:  # ₹500 to ₹50 lakhs
    prices.append(price)
```

### Customizing Search Behavior

Edit the decision prompt in `transaction_parser_node`:

```python
decision_prompt = f"""
Based on this user message, should we search for the product price online?

User message: "{raw_text}"

If the message mentions a specific product (like iPhone, MacBook, laptop, etc.) 
that typically has a known market price, you should use the search_product_price tool.

If it's a generic expense or service (like "food", "groceries", "uber ride") 
without a specific product, don't search.
"""
```

## Limitations

### What It Can Do
✅ Search for popular products  
✅ Extract prices from search results  
✅ Handle Indian rupee formats  
✅ Filter unrealistic prices  
✅ Provide estimated prices for recommendations  

### What It Cannot Do
❌ Guarantee 100% accurate prices (prices change)  
❌ Find prices for very niche products  
❌ Account for discounts/offers  
❌ Differentiate between variants (128GB vs 256GB)  
❌ Work offline  

## Best Practices

### For Users

1. **Provide amount when known**
   - More accurate recommendations
   - Faster processing

2. **Be specific about product**
   - Good: "iPhone 15 Pro 256GB"
   - Bad: "new phone"

3. **Understand it's an estimate**
   - Actual price may vary
   - Check before purchase

### For Developers

1. **Cache search results**
   - Avoid repeated searches for same product
   - Implement TTL (time-to-live)

2. **Add more search sources**
   - Amazon India API
   - Flipkart API
   - Price comparison sites

3. **Improve extraction**
   - Use LLM to extract price from text
   - Handle more price formats

## Error Handling

### Search Fails
```python
try:
    search_results = search_product_price(product_name)
except Exception as e:
    print(f"⚠️ Web search failed: {e}")
    # Continue with amount = 0
```

### No Price Found
```python
if estimated_price == 0:
    print(f"⚠️ Could not find price online. Using amount = 0")
    # User will be prompted to provide amount
```

### Network Issues
- System gracefully falls back to amount = 0
- User can retry or provide amount manually

## Future Enhancements

### Planned Features

1. **Price Caching**
   ```python
   # Cache prices for 24 hours
   cache = {
       "iPhone 15": {"price": 79900, "timestamp": "2024-01-15"}
   }
   ```

2. **Multiple Sources**
   ```python
   # Check multiple sources and average
   amazon_price = get_amazon_price(product)
   flipkart_price = get_flipkart_price(product)
   avg_price = (amazon_price + flipkart_price) / 2
   ```

3. **Variant Detection**
   ```python
   # Detect storage/color variants
   "iPhone 15 Pro 256GB" → Search specifically
   "iPhone 15 Pro" → Ask user for variant
   ```

4. **Price History**
   ```python
   # Show if price is good deal
   "Current: ₹79,900 (10% below average)"
   ```

## Testing

### Test Web Search

```bash
# Install dependencies
pip install duckduckgo-search

# Test search
python -c "
from app.tools.web_search import search_product_price, extract_price_from_search
results = search_product_price('iPhone 15')
price = extract_price_from_search(results, 'iPhone 15')
print(f'Estimated price: ₹{price}')
"
```

### Test Transaction Parser

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I want to buy an iPhone 15",
    "user": {
      "id": "test_user",
      "name": "Test",
      "email": "test@test.com"
    }
  }'
```

**Expected logs:**
```
💰 Amount not provided. Searching for price online...
✅ Found estimated price: ₹79,900
```

## Dependencies

```
tavily-python  # Tavily API for web search
langchain-community  # Tool integration
langchain-openai  # LLM with tool binding
```

Install:
```bash
pip install tavily-python langchain-community langchain-openai
```

API Key:
```python
# Set in app/tools/web_search.py or .env
os.environ["TAVILY_API_KEY"] = "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"
```

## Summary

The web search pricing feature uses an intelligent LLM-powered decision engine to automatically find product prices when users don't provide them. No hardcoded keywords - the LLM understands context and decides when to search.

**Key Benefits:**
- ✅ Intelligent decision making (no keyword lists to maintain)
- ✅ Better user experience (just say "I'm buying an iPhone 15")
- ✅ More accurate recommendations
- ✅ Handles expensive products intelligently
- ✅ Reduces user friction
- ✅ Uses Tavily API for reliable search results

**How It Works:**
1. User mentions a product without price
2. LLM analyzes the message
3. LLM decides if search is needed
4. If yes, searches Tavily for price
5. Extracts price and uses for recommendation

**Example:**
```
User: "I want to buy an iPhone 15"
System: 🤖 LLM decided to search for price...
        🔍 Searching for: iPhone 15
        ✅ Found estimated price: ₹79,900
        💳 Best Card: HDFC Regalia Gold (2,698 points)
```
