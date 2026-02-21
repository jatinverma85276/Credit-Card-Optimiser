# User-Specific Credit Card System

## Overview

The system is now fully user-specific. Each user has their own isolated:
- Credit card portfolio
- Transaction history
- Long-term memory (LTM)
- Conversation threads

## Key Changes

### 1. Database Schema Updates

#### Users Table (NEW)
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR UNIQUE NOT NULL,
    name VARCHAR NOT NULL,
    email VARCHAR UNIQUE NOT NULL,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

#### Credit Cards Table (UPDATED)
```sql
ALTER TABLE credit_cards 
ADD COLUMN user_id VARCHAR;

-- Removed unique constraint on card_name
-- Multiple users can now have the same card
```

#### Chat Threads Table (UPDATED)
```sql
ALTER TABLE chat_threads 
ADD COLUMN user_id VARCHAR;
```

### 2. User Flow

#### First-Time User Journey

**Step 1: User logs in and asks a question**
```json
POST /chat
{
  "message": "I'm spending 2399 on Myntra",
  "user": {
    "id": "user_1771606239250",
    "name": "Jatin",
    "email": "jatinv85276@gmail.com"
  }
}
```

**System Actions:**
1. Creates user profile in database
2. Checks if user has any credit cards
3. Since no cards exist, responds with:

```
"You don't have any credit cards registered yet. Please add your credit cards first using the /add_card command to get personalized recommendations.

Example: /add_card HDFC Regalia Gold Card with 5x rewards on dining..."
```

**Step 2: User adds their credit cards**
```json
POST /chat
{
  "message": "/add_card HDFC Regalia Gold Card. Annual fee: Rs 2500. Rewards: 4 points per Rs 150 on all spends. 5X rewards on travel and dining.",
  "user": {
    "id": "user_1771606239250",
    "name": "Jatin",
    "email": "jatinv85276@gmail.com"
  }
}
```

**System Actions:**
1. Parses card details using LLM
2. Saves card to database with `user_id = "user_1771606239250"`
3. Responds: "✅ HDFC Regalia Gold Card added successfully to your cards database."

**Step 3: User asks for recommendation**
```json
POST /chat
{
  "message": "I'm spending 5000 on Swiggy",
  "user": {
    "id": "user_1771606239250",
    "name": "Jatin",
    "email": "jatinv85276@gmail.com"
  }
}
```

**System Actions:**
1. Fetches ONLY this user's credit cards
2. Calculates rewards for each card
3. Recommends the best card from their portfolio
4. Saves transaction to user's history

### 3. Memory Isolation

#### Transaction History
- Stored with `user_id`
- Semantic search only retrieves user's own transactions
- Used for context in recommendations

#### General Memories
- User preferences, facts, and context
- Stored with `user_id`
- Retrieved only for that specific user

#### Credit Cards
- Each user has their own portfolio
- Same card can exist for multiple users
- Recommendations based only on user's cards

### 4. API Endpoints

#### Get User's Credit Cards
```bash
GET /user/{user_id}/cards
```

Returns all credit cards registered by this user.

#### Get User's Threads
```bash
GET /user/{user_id}/threads
```

Returns all conversation threads for this user.

#### Get User Profile
```bash
GET /user/{user_id}
```

Returns user information.

## Implementation Details

### Graph State
```python
class GraphState(TypedDict):
    messages: Annotated[list, add_messages]
    user_id: str  # NEW: User identification
    # ... other fields
```

### Node Updates

#### fetch_user_cards_node
- Now accepts `config: RunnableConfig`
- Extracts `user_id` from config
- Fetches only that user's cards
- If no cards found, prompts user to add cards

#### add_card_node
- Now accepts `config: RunnableConfig`
- Extracts `user_id` from config
- Saves card with user_id

#### transaction_parser_node
- Already uses `user_id` from config
- Saves transactions with user_id

### Repository Functions

```python
def add_card(db: Session, card: CreditCard, user_id: str):
    # Saves card with user_id
    
def get_user_cards(db: Session, user_id: str):
    # Returns only user's cards
```

## Migration Steps

### Step 1: Run User Migration
```bash
python migrate_add_users.py
```

Creates:
- `users` table
- `user_id` column in `chat_threads`

### Step 2: Run Cards Migration
```bash
python migrate_add_user_to_cards.py
```

Updates:
- Adds `user_id` column to `credit_cards`
- Removes unique constraint on `card_name`
- Updates existing data with "default_user"

## Testing the System

### Test 1: New User Without Cards
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I want to spend 5000 on Amazon",
    "user": {
      "id": "test_user_1",
      "name": "Test User",
      "email": "test@example.com"
    }
  }'
```

Expected: Prompt to add credit cards

### Test 2: Add Card
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "/add_card HDFC Regalia Gold Card. 5X rewards on dining and travel.",
    "user": {
      "id": "test_user_1",
      "name": "Test User",
      "email": "test@example.com"
    }
  }'
```

Expected: Card added successfully

### Test 3: Get Recommendation
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I want to spend 5000 on Swiggy",
    "user": {
      "id": "test_user_1",
      "name": "Test User",
      "email": "test@example.com"
    }
  }'
```

Expected: Recommendation based on user's cards

### Test 4: User Isolation
```bash
# Different user with same question
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I want to spend 5000 on Swiggy",
    "user": {
      "id": "test_user_2",
      "name": "Another User",
      "email": "another@example.com"
    }
  }'
```

Expected: Prompt to add cards (different user, no cards)

## Benefits

1. **Privacy**: Users can't see each other's cards or transactions
2. **Personalization**: Recommendations based on user's actual cards
3. **Scalability**: System can handle multiple users simultaneously
4. **Accuracy**: No confusion between different users' portfolios
5. **Smart Prompting**: System guides new users to add cards first

## Important Notes

- `user.id` is the primary identifier for all user-specific data
- The system automatically creates user profiles on first chat
- Credit cards are private to each user
- Transaction history is isolated per user
- LTM (Long-Term Memory) is user-specific
- Same card can exist for multiple users (e.g., "HDFC Regalia Gold")
