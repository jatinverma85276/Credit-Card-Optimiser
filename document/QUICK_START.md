# Quick Start: User-Specific Credit Card System

## 🚀 Setup (5 minutes)

### 1. Run Migrations
```bash
python migrate_add_users.py
python migrate_add_user_to_cards.py
```

### 2. Start Server
```bash
uvicorn main:app --reload
```

### 3. Test Health
```bash
curl http://localhost:8000/health
```

## 💡 How It Works

### First-Time User Journey

**1. User asks a question (no cards yet)**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I want to spend 5000 on Amazon",
    "user": {
      "id": "user_123",
      "name": "John Doe",
      "email": "john@example.com"
    }
  }'
```

**Response:**
```
"You don't have any credit cards registered yet. Please add your credit cards first..."
```

**2. User adds their credit card**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "/add_card HDFC Regalia Gold Card. Annual fee Rs 2500. 5X rewards on dining and travel. 4 points per Rs 150 on all other spends.",
    "user": {
      "id": "user_123",
      "name": "John Doe",
      "email": "john@example.com"
    }
  }'
```

**Response:**
```
"✅ HDFC Regalia Gold Card added successfully to your cards database."
```

**3. User gets personalized recommendation**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I want to spend 3000 on Swiggy",
    "user": {
      "id": "user_123",
      "name": "John Doe",
      "email": "john@example.com"
    }
  }'
```

**Response:**
```
"💳 Best Card Recommendation

Use HDFC Regalia Gold Card for this transaction at Swiggy.

🎯 You'll earn approximately 300 reward points
⚡ Reward Rate: 5x (Dining)

Smart choice for maximizing rewards!"
```

## 📋 Key Endpoints

### Chat
```bash
POST /chat
Body: { "message": "...", "user": { "id": "...", "name": "...", "email": "..." } }
```

### Get User's Threads
```bash
GET /user/{user_id}/threads
```

### Get Thread History
```bash
GET /chat/history/{thread_id}
```

### Delete Thread
```bash
DELETE /chat/thread/{thread_id}
```

### Get User Info
```bash
GET /user/{user_id}
```

## 🎯 Key Features

✅ **User Isolation** - Each user has their own cards and data  
✅ **Smart Prompting** - System guides users to add cards first  
✅ **Personalized Recommendations** - Based on user's actual cards  
✅ **Long-Term Memory** - Remembers user preferences and history  
✅ **Multi-Session** - Context maintained across conversations  

## 🔑 Important Notes

1. **User Object Required**: Every chat request must include user info
2. **Add Cards First**: Users must add cards before getting recommendations
3. **User-Specific**: Each user only sees their own cards and data
4. **Same Card, Different Users**: Multiple users can have the same card name

## 📚 More Documentation

- **API_REFERENCE.md** - Complete API documentation
- **USER_SPECIFIC_SYSTEM.md** - Technical architecture
- **MIGRATION_GUIDE.md** - Detailed migration steps
- **CHANGES_SUMMARY.md** - All changes made

## 🐛 Troubleshooting

### Issue: "Service not initialized"
**Solution:** Check if server started successfully and database is connected

### Issue: "No cards found"
**Solution:** User needs to add cards first using `/add_card` command

### Issue: Migration fails
**Solution:** Check MIGRATION_GUIDE.md for detailed troubleshooting

## 🎓 Example Flow

```javascript
// Frontend example
const user = {
  id: "user_1771606239250",
  name: "Jatin",
  email: "jatinv85276@gmail.com"
};

// 1. First chat - will prompt to add cards
await fetch('/chat', {
  method: 'POST',
  body: JSON.stringify({
    message: "I'm spending 2399 on Myntra",
    user: user
  })
});

// 2. Add card
await fetch('/chat', {
  method: 'POST',
  body: JSON.stringify({
    message: "/add_card HDFC Regalia Gold Card. 5X rewards on dining...",
    user: user
  })
});

// 3. Get recommendation
await fetch('/chat', {
  method: 'POST',
  body: JSON.stringify({
    message: "I'm spending 5000 on Swiggy",
    user: user
  })
});

// 4. Get user's threads
await fetch(`/user/${user.id}/threads`);
```

## ✨ That's It!

You're ready to use the user-specific credit card optimization system!
