# Migration Guide: User-Specific System

## Overview
This guide will help you migrate your existing system to support user-specific credit cards and memories.

## Prerequisites
- Backup your database before running migrations
- Ensure your application is stopped during migration
- Python environment with all dependencies installed

## Step-by-Step Migration

### Step 1: Backup Database
```bash
# For PostgreSQL
pg_dump your_database > backup_$(date +%Y%m%d).sql

# Or use your preferred backup method
```

### Step 2: Run User Migration
```bash
python migrate_add_users.py
```

**What this does:**
- Creates `users` table
- Adds `user_id` column to `chat_threads` table
- Creates necessary indexes
- Updates existing threads with "default_user"

**Expected Output:**
```
✅ Migration completed successfully!
✅ Created users table
✅ Added user_id to chat_threads table
✅ Updated existing threads with default_user
```

### Step 3: Run Credit Cards Migration
```bash
python migrate_add_user_to_cards.py
```

**What this does:**
- Adds `user_id` column to `credit_cards` table
- Removes unique constraint on `card_name`
- Creates index on `user_id`
- Updates existing cards with "default_user"

**Expected Output:**
```
✅ Migration completed successfully!
✅ Added user_id to credit_cards table
✅ Removed unique constraint on card_name
✅ Updated existing cards with default_user
```

### Step 4: Verify Migration
```bash
# Connect to your database and verify
psql your_database

# Check users table
\d users

# Check credit_cards table has user_id
\d credit_cards

# Check chat_threads table has user_id
\d chat_threads

# Verify data
SELECT * FROM users LIMIT 5;
SELECT card_name, user_id FROM credit_cards LIMIT 5;
SELECT thread_id, user_id FROM chat_threads LIMIT 5;
```

### Step 5: Restart Application
```bash
# Start your FastAPI server
uvicorn main:app --reload
```

### Step 6: Test the System

#### Test 1: Health Check
```bash
curl http://localhost:8000/health
```

Expected: `{"status": "healthy", "database": "connected", "graph": "initialized"}`

#### Test 2: New User Chat
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I want to spend 5000 on Amazon",
    "user": {
      "id": "test_user_123",
      "name": "Test User",
      "email": "test@example.com"
    }
  }'
```

Expected: Prompt to add credit cards (since new user has no cards)

#### Test 3: Add Credit Card
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "/add_card HDFC Regalia Gold Card. Annual fee Rs 2500. 5X rewards on dining and travel.",
    "user": {
      "id": "test_user_123",
      "name": "Test User",
      "email": "test@example.com"
    }
  }'
```

Expected: "✅ HDFC Regalia Gold Card added successfully to your cards database."

#### Test 4: Get Recommendation
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I want to spend 3000 on Swiggy",
    "user": {
      "id": "test_user_123",
      "name": "Test User",
      "email": "test@example.com"
    }
  }'
```

Expected: Card recommendation based on user's portfolio

#### Test 5: Get User's Threads
```bash
curl http://localhost:8000/user/test_user_123/threads
```

Expected: List of threads for this user

## Rollback Plan

If something goes wrong, you can rollback:

### Rollback Step 1: Restore Database
```bash
# For PostgreSQL
psql your_database < backup_YYYYMMDD.sql
```

### Rollback Step 2: Revert Code Changes
```bash
git checkout HEAD~1  # Or your previous commit
```

## Common Issues

### Issue 1: Migration Script Fails
**Error:** `relation "users" already exists`

**Solution:** The table already exists. You can skip this migration or drop the table first:
```sql
DROP TABLE IF EXISTS users CASCADE;
```

### Issue 2: Existing Cards Not Visible
**Problem:** Old cards added before migration are not showing up

**Solution:** They're assigned to "default_user". You can:
1. Reassign them to a specific user:
```sql
UPDATE credit_cards 
SET user_id = 'your_user_id' 
WHERE user_id = 'default_user';
```

2. Or have users re-add their cards

### Issue 3: Unique Constraint Error
**Error:** `duplicate key value violates unique constraint "credit_cards_card_name_key"`

**Solution:** The migration should have removed this constraint. Run:
```sql
ALTER TABLE credit_cards DROP CONSTRAINT IF EXISTS credit_cards_card_name_key;
```

## Post-Migration Checklist

- [ ] Database backup completed
- [ ] Both migrations ran successfully
- [ ] Application starts without errors
- [ ] Health check passes
- [ ] New user can register
- [ ] User can add credit cards
- [ ] User gets recommendations
- [ ] User isolation works (different users see different cards)
- [ ] Existing data preserved (if applicable)

## Data Migration for Existing Users

If you have existing users and want to migrate their data:

```python
# migration_script.py
from app.db.database import SessionLocal
from app.db.models import User, CreditCardModel, ChatThread

db = SessionLocal()

# Example: Migrate cards from default_user to specific users
# You'll need to determine which cards belong to which users

# Create users
user1 = User(user_id="user_001", name="John Doe", email="john@example.com")
db.add(user1)

# Reassign cards
db.query(CreditCardModel).filter(
    CreditCardModel.card_name.in_(["HDFC Regalia", "SBI Cashback"])
).update({"user_id": "user_001"})

# Reassign threads
db.query(ChatThread).filter(
    ChatThread.thread_id.in_(["thread_1", "thread_2"])
).update({"user_id": "user_001"})

db.commit()
db.close()
```

## Support

If you encounter issues:
1. Check the error logs
2. Verify database schema matches expected structure
3. Ensure all dependencies are installed
4. Check that environment variables are set correctly

## Next Steps

After successful migration:
1. Update your frontend to send user information with each request
2. Test thoroughly with multiple users
3. Monitor for any issues
4. Consider adding user authentication/authorization
5. Update documentation for your team
