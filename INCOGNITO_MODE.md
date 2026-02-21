# Incognito Mode Documentation

## Overview

Incognito mode allows users to interact with the credit card optimizer without saving any conversation history or transaction data. This provides privacy for sensitive queries while still allowing access to card recommendations.

## What Gets Saved in Normal Mode vs Incognito Mode

### Normal Mode (incognito=false)
✅ Conversation history saved  
✅ Transaction memory saved (for future context)  
✅ Thread metadata saved  
✅ User can retrieve chat history later  
✅ LTM (Long-Term Memory) learns from transactions  

### Incognito Mode (incognito=true)
❌ No conversation history saved  
❌ No transaction memory saved  
❌ No thread metadata saved  
✅ User can still get card recommendations  
✅ User's registered cards are still accessible  
✅ Real-time recommendations work normally  

## How to Use

### API Request

Add `"incognito": true` to your chat request:

```json
{
  "message": "I want to spend 5000 on Amazon",
  "user": {
    "id": "user_123",
    "name": "John Doe",
    "email": "john@example.com"
  },
  "incognito": true
}
```

### Example: Normal Mode

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I want to spend 5000 on Swiggy",
    "user": {
      "id": "user_123",
      "name": "John Doe",
      "email": "john@example.com"
    },
    "incognito": false
  }'
```

**Result:**
- Conversation saved ✅
- Transaction saved to memory ✅
- Can retrieve history later ✅

### Example: Incognito Mode

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I want to spend 5000 on Swiggy",
    "user": {
      "id": "user_123",
      "name": "John Doe",
      "email": "john@example.com"
    },
    "incognito": true
  }'
```

**Result:**
- Gets card recommendation ✅
- No conversation saved ❌
- No transaction saved ❌
- Cannot retrieve history ❌

## Use Cases

### When to Use Incognito Mode

1. **Privacy-Sensitive Queries**
   - "I'm planning a surprise gift purchase"
   - "Which card for adult content subscriptions?"
   - "Best card for medical expenses?"

2. **Testing/Exploration**
   - "What if I spend 100k on travel?"
   - Testing different scenarios without polluting history

3. **Shared Devices**
   - Using on a friend's device
   - Public computer/kiosk

4. **One-Time Queries**
   - Quick recommendation without saving context
   - Temporary what-if scenarios

### When to Use Normal Mode

1. **Regular Usage**
   - Building transaction history for better recommendations
   - Want to review past conversations

2. **Learning from Patterns**
   - System learns your spending patterns
   - Better future recommendations

3. **Multi-Session Context**
   - Continue conversations across sessions
   - Reference past transactions

## Technical Implementation

### Architecture

```
Normal Mode:
User Request → Graph (with PostgresSaver) → Save to DB → Response

Incognito Mode:
User Request → Graph (no checkpointer) → Skip DB save → Response
```

### What Happens Internally

1. **Graph Selection**
   - Normal: Uses `graph` (with PostgresSaver checkpointer)
   - Incognito: Uses `graph_incognito` (no checkpointer)

2. **Thread ID**
   - Normal: Regular thread_id or generated UUID
   - Incognito: Prefixed with `incognito_` (not saved)

3. **Transaction Parser**
   - Normal: Saves transaction to vector DB
   - Incognito: Skips `save_transaction_memory()`

4. **Thread Metadata**
   - Normal: Saved to `chat_threads` table
   - Incognito: Skipped entirely

## Frontend Integration

### React/JavaScript Example

```javascript
// Normal mode
async function sendMessage(message, user) {
  const response = await fetch('/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message,
      user,
      incognito: false  // Normal mode
    })
  });
  return await response.json();
}

// Incognito mode
async function sendIncognitoMessage(message, user) {
  const response = await fetch('/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message,
      user,
      incognito: true  // Incognito mode
    })
  });
  return await response.json();
}
```

### UI Toggle Example

```javascript
const [incognitoMode, setIncognitoMode] = useState(false);

function ChatInterface() {
  return (
    <div>
      <label>
        <input
          type="checkbox"
          checked={incognitoMode}
          onChange={(e) => setIncognitoMode(e.target.checked)}
        />
        Incognito Mode 🕵️
      </label>
      
      <button onClick={() => sendMessage(message, user, incognitoMode)}>
        Send
      </button>
    </div>
  );
}
```

## Limitations

### What Incognito Mode Does NOT Do

❌ **Does not hide user identity**
- User info is still passed in the request
- System knows who is making the query

❌ **Does not prevent card access**
- User's registered cards are still accessible
- Recommendations still based on user's cards

❌ **Does not encrypt messages**
- Messages are transmitted normally
- Use HTTPS for transport security

❌ **Does not prevent logging**
- Server logs may still record requests
- Use for privacy from history, not from admins

### What IS Protected

✅ Conversation history not saved to database  
✅ Transaction patterns not recorded  
✅ No thread metadata stored  
✅ Cannot be retrieved later via `/chat/history`  
✅ Won't appear in `/user/{user_id}/threads`  

## Comparison Table

| Feature | Normal Mode | Incognito Mode |
|---------|-------------|----------------|
| Card Recommendations | ✅ Yes | ✅ Yes |
| Save Conversation | ✅ Yes | ❌ No |
| Save Transactions | ✅ Yes | ❌ No |
| Retrieve History | ✅ Yes | ❌ No |
| LTM Learning | ✅ Yes | ❌ No |
| Thread Metadata | ✅ Saved | ❌ Not Saved |
| User Cards Access | ✅ Yes | ✅ Yes |
| Real-time Recommendations | ✅ Yes | ✅ Yes |

## Security Considerations

### What Incognito Mode Protects

1. **Database Privacy**
   - No records in `chat_threads` table
   - No records in `transaction_history` table
   - No records in `checkpoints` table

2. **History Privacy**
   - Cannot retrieve via API later
   - Won't show up in user's thread list
   - No persistent memory of the conversation

### What It Doesn't Protect

1. **Server Logs**
   - Application logs may still record requests
   - Web server access logs

2. **Network Traffic**
   - Messages transmitted over network
   - Use HTTPS for encryption

3. **User Authentication**
   - User is still identified
   - Not anonymous

## Best Practices

### For Users

1. **Use incognito for sensitive queries**
   - Personal purchases
   - Medical expenses
   - Gifts/surprises

2. **Use normal mode for regular usage**
   - Better recommendations over time
   - Can review past conversations

3. **Don't rely on incognito for anonymity**
   - You're still authenticated
   - Use for privacy from history only

### For Developers

1. **Respect incognito flag everywhere**
   - Check in all nodes that save data
   - Don't log sensitive info

2. **Clear indication in UI**
   - Show incognito status clearly
   - Warn users about limitations

3. **Audit logging**
   - Consider separate audit logs
   - Balance security with privacy

## Testing

### Test Normal Mode
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Test normal mode",
    "user": {"id": "test_user", "name": "Test", "email": "test@test.com"},
    "incognito": false,
    "thread_id": "test_thread_123"
  }'

# Verify saved
curl http://localhost:8000/chat/history/test_thread_123
# Should return the conversation
```

### Test Incognito Mode
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Test incognito mode",
    "user": {"id": "test_user", "name": "Test", "email": "test@test.com"},
    "incognito": true
  }'

# Try to retrieve (should fail)
curl http://localhost:8000/chat/history/incognito_*
# Should return 404 or empty
```

## Summary

Incognito mode provides a privacy-focused way to use the credit card optimizer without leaving a trace in the database. It's perfect for sensitive queries while still providing full recommendation functionality based on the user's registered cards.

**Key Points:**
- ✅ Full functionality for recommendations
- ❌ No data persistence
- 🕵️ Privacy from history, not anonymity
- 🎯 Use for sensitive or one-time queries
