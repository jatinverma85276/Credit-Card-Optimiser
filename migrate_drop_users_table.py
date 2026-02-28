"""
Migration script to drop the redundant users table
The user_auth table now serves as the single source of truth for user data
Run this once to clean up your database schema
"""
from sqlalchemy import text
from app.db.database import engine

def migrate():
    with engine.connect() as conn:
        # Drop the users table (user_auth is now the single source of truth)
        conn.execute(text("""
            DROP TABLE IF EXISTS users CASCADE;
        """))
        
        conn.commit()
        print("✅ Migration completed successfully!")
        print("✅ Dropped users table")
        print("✅ user_auth table is now the single source of truth for user data")

if __name__ == "__main__":
    migrate()
