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

1. **First Chat**: User sends message with their info
   - System creates user profile in database
   - Uses `user.id` as LTM identifier
   - All memories are tagged with this user_id

2. **Subsequent Chats**: Same user, different sessions
   - System recognizes user by `user.id`
   - Retrieves user-specific memories across all threads
   - Maintains personalized context

3. **Memory Isolation**: Each user has separate:
   - Transaction history
   - General memories (preferences, facts)
   - Credit card recommendations
   - Conversation threads

---

## Migration Required

Before using the new user system, run the migration:

```bash
python migrate_add_users.py
```

This will:
- Create the `users` table
- Add `user_id` column to `chat_threads`
- Update existing threads with "default_user"

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
curl http://localhost:8000/chat/threads?user_id=user_123
```

### 4. Delete a thread
```bash
curl -X DELETE http://localhost:8000/chat/thread/abc-123
```
