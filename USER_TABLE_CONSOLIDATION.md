# User Table Consolidation Summary

## Problem
The application had two redundant user tables:
- `users` table (via `User` model)
- `user_auth` table (via `UserAuth` model)

Both tables stored similar user information, causing confusion and potential data inconsistency.

## Solution
Consolidated to use only the `user_auth` table as the single source of truth for user data.

## Changes Made

### 1. Database Models (`app/db/models.py`)
- ✅ Removed the `User` class/model
- ✅ Kept `UserAuth` class as the single user model
- ✅ Updated `ChatThread` comment to reference `UserAuth` instead of `User`

### 2. Main API (`main.py`)
- ✅ Updated import: `from app.db.models import ChatThread, UserAuth` (removed `User`)
- ✅ Updated `/user/{user_id}` endpoint to query `UserAuth` instead of `User`
- ✅ Updated `/chat` endpoint to check `UserAuth` for existing users (no longer creates users in chat endpoint)
- ✅ Simplified user update logic - now only updates name if changed

### 3. Documentation (`document/MIGRATION_GUIDE.md`)
- ✅ Updated example code to use `UserAuth` instead of `User`

### 4. Migration Script
- ✅ Created `migrate_drop_users_table.py` to drop the redundant `users` table

## Database Migration

To apply these changes to your database, run:

```bash
python migrate_drop_users_table.py
```

This will:
- Drop the `users` table
- Keep the `user_auth` table as the single source of truth

## Important Notes

1. **User Creation**: Users are now only created through the `/auth/signup` endpoint, which creates entries in the `user_auth` table with hashed passwords.

2. **User Authentication**: All authentication flows use the `UserAuth` model with proper password hashing.

3. **User Queries**: All user lookups now query the `user_auth` table.

4. **No Breaking Changes**: The API endpoints remain the same, only the internal implementation changed.

## Verification

All files pass diagnostics with no errors:
- ✅ `app/db/models.py`
- ✅ `main.py`
- ✅ `app/services/auth_service.py`

## Files Modified
1. `app/db/models.py` - Removed User model
2. `main.py` - Updated to use UserAuth
3. `document/MIGRATION_GUIDE.md` - Updated documentation
4. `migrate_drop_users_table.py` - New migration script
