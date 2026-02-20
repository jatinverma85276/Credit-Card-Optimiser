# Credit Card Optimizer API Reference

## User Management & Authentication

### Chat with User Context
**POST** `/chat`

Send a message with user information. The system automatically:
- Creates/updates user profile
- Uses user.id for personalized Long-Term Memory (LTM)
- Links conversations to the user

**Request Body:**
```json
{
  "message": "What's the best card for travel?",
  "thread_id": "optional-thread-id",
  "user": {
    "id": "user_1771606239250",
    "name": "Jatin",
    "email": "jatinv85276@gmail.com"
  },
  "stream": false
}
```

**Response:**
```json
{
  "response": "Based on your profile...",
  "thread_id": "abc-123-def"
}
```

**Key Features:**
- `user.id` is used as the LTM identifier (replaces "default_user")
- Each user has isolated memory and preferences
- First-time users are automatically registered
- User info is updated if name/email changes

---

## User Endpoints

### Get User Information
**GET** `/user/{user_id}`

Retrieve user profile information.

**Response:**
```json
{
  "user_id": "user_1771606239250",
  "name": "Jatin",
  "email": "jatinv85276@gmail.com",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### Get User's Thread IDs
**GET** `/user/{user_id}/threads`

Get all threads for a specific user with detailed information.

**Response:**
```json
{
  "threads": [
    {
      "thread_id": "3f53f17f-1bb7-08-5a878",
      "thread_name": "What's my name ?",
      "created_at": "2026-02-18T16:31:56.175449+05:30",
      "updated_at": "2026-02-18T16:31:56.175449+05:30"
    },
    {
      "thread_id": "3f53f17f-1bb7-4083-bc03-6e49a5660d5a",
      "thread_name": "Trip to Goa",
      "created_at": "2026-02-18T15:58:02.991470+05:30",
      "updated_at": "2026-02-18T15:58:02.991470+05:30"
    }
  ],
  "count": 2
}
```

---

## Thread/Session Management

### Get All Threads (with optional user filter)
**GET** `/chat/threads?user_id={user_id}`

Get all conversation threads, optionally filtered by user.

**Query Parameters:**
- `user_id` (optional): Filter threads for a specific user

**Response:**
```json
{
  "threads": [
    {
      "thread_id": "abc-123",
      "thread_name": "What's the best card for travel?",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:35:00Z"
    }
  ],
  "count": 1
}
```

### Get Thread History
**GET** `/chat/history/{thread_id}`

Get conversation history for a specific thread.

**Response:**
```json
{
  "thread_id": "abc-123",
  "messages": [
    {
      "role": "user",
      "content": "What's the best card for travel?"
    },
    {
      "role": "assistant",
      "content": "Based on your profile..."
    }
  ]
}
```

### Delete Thread
**DELETE** `/chat/thread/{thread_id}`

Delete a conversation thread and all its history.

**Response:**
```json
{
  "message": "Thread abc-123 deleted successfully",
  "thread_id": "abc-123",
  "deleted": {
    "thread_metadata": true,
    "checkpoints": true
  }
}
```

---

## Health Check

### Check Service Status
**GET** `/health`

Verify server and database connectivity.

**Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "graph": "initialized"
}
```

---

## How User-Specific LTM Works

### Complete User Isolation

Each user has their own:
1. **Credit Cards Portfolio**: Cards added by one user are not visible to others
2. **Transaction History**: Past transactions are user-specific
3. **General Memories**: Preferences, facts, and context
4. **Conversation Threads**: Chat history and sessions

### First-Time User Flow

1. **User logs in and starts first chat**:
   ```json
   {
     "message": "I'm spending 2399 on Myntra",
     "user": {
       "id": "user_123",
       "name": "Jatin",
       "email": "jatin@example.com"
     }
   }
   ```

2. **System Response**:
   - Creates user profile
   - Checks if user has any credit cards
   - If NO cards found: Prompts user to add cards
   - If cards exist: Provides recommendation

3. **Expected Response for New User**:
   ```
   "You don't have any credit cards registered yet. Please add your credit cards first using the /add_card command to get personalized recommendations.
   
   Example: /add_card HDFC Regalia Gold Card with 5x rewards on dining..."
   ```

### Adding Credit Cards

Users must add their own credit cards to get recommendations:

```json
{
  "message": "/add_card HDFC Regalia Gold Card. Annual fee: Rs 2500. Rewards: 4 points per Rs 150 on all spends. 5X rewards on travel and dining. Welcome bonus: 10000 points.",
  "user": {
    "id": "user_123",
    "name": "Jatin",
    "email": "jatin@example.com"
  }
}
```

### Getting Recommendations

Once cards are added, the system provides personalized recommendations:

```json
{
  "message": "I'm spending 5000 on Swiggy",
  "user": {
    "id": "user_123",
    "name": "Jatin",
    "email": "jatin@example.com"
  }
}
```

Response will compare ONLY the user's registered cards and recommend the best one.

---

## Migration Required

Before using the new user system, run BOTH migrations in order:

```bash
# Step 1: Add users table and update chat_threads
python migrate_add_users.py

# Step 2: Add user_id to credit_cards table
python migrate_add_user_to_cards.py
```

This will:
- Create the `users` table
- Add `user_id` column to `chat_threads`
- Add `user_id` column to `credit_cards`
- Remove unique constraint on card_name (multiple users can have same card)
- Update existing data with "default_user"

---

## Example Usage Flow

### 1. First-time user starts a chat
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I want to optimize my credit cards",
    "user": {
      "id": "user_123",
      "name": "John Doe",
      "email": "john@example.com"
    }
  }'
```

### 2. Continue conversation in same thread
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What about travel rewards?",
    "thread_id": "abc-123",
    "user": {
      "id": "user_123",
      "name": "John Doe",
      "email": "john@example.com"
    }
  }'
```

### 3. Get user's threads
```bash
# Get all threads for a user with detailed info
curl http://localhost:8000/user/user_123/threads

# Alternative: Get threads with query parameter (same result)
curl http://localhost:8000/chat/threads?user_id=user_123
```

### 4. Delete a thread
```bash
curl -X DELETE http://localhost:8000/chat/thread/abc-123
```
