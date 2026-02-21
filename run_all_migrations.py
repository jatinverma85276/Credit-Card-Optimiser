"""
Run all migrations in the correct order
"""
import sys

print("=" * 60)
print("Running All Migrations")
print("=" * 60)

# Migration 1: Add users table
print("\n[1/3] Running migrate_add_users.py...")
try:
    from migrate_add_users import migrate as migrate_users
    migrate_users()
except Exception as e:
    print(f"❌ Migration 1 failed: {e}")
    sys.exit(1)

# Migration 2: Add user_id to credit_cards
print("\n[2/3] Running migrate_add_user_to_cards.py...")
try:
    from migrate_add_user_to_cards import migrate as migrate_cards
    migrate_cards()
except Exception as e:
    print(f"❌ Migration 2 failed: {e}")
    sys.exit(1)

# Migration 3: Add authentication table
print("\n[3/3] Running migrate_add_auth.py...")
try:
    from migrate_add_auth import migrate as migrate_auth
    migrate_auth()
except Exception as e:
    print(f"❌ Migration 3 failed: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ All migrations completed successfully!")
print("=" * 60)
print("\nYou can now:")
print("1. Test signup: POST /auth/signup")
print("2. Test login: POST /auth/login")
print("3. Use chat with authenticated users")
print("\nServer is running at: http://127.0.0.1:8000")
print("API docs at: http://127.0.0.1:8000/docs")
