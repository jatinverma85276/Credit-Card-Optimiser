"""
Migration script to add User table and update ChatThread table with user_id
Run this once to update your database schema
"""
from sqlalchemy import text
from app.db.database import engine

def migrate():
    with engine.connect() as conn:
        # Create users table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                user_id VARCHAR UNIQUE NOT NULL,
                name VARCHAR NOT NULL,
                email VARCHAR UNIQUE NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """))
        
        # Create index on user_id
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_users_user_id ON users(user_id);
        """))
        
        # Create index on email
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
        """))
        
        # Add user_id column to chat_threads if it doesn't exist
        conn.execute(text("""
            DO $$ 
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='chat_threads' AND column_name='user_id'
                ) THEN
                    ALTER TABLE chat_threads ADD COLUMN user_id VARCHAR;
                END IF;
            END $$;
        """))
        
        # Create index on chat_threads.user_id
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_chat_threads_user_id ON chat_threads(user_id);
        """))
        
        # Update existing threads to have a default user_id (optional)
        conn.execute(text("""
            UPDATE chat_threads 
            SET user_id = 'default_user' 
            WHERE user_id IS NULL;
        """))
        
        conn.commit()
        print("✅ Migration completed successfully!")
        print("✅ Created users table")
        print("✅ Added user_id to chat_threads table")
        print("✅ Updated existing threads with default_user")

if __name__ == "__main__":
    migrate()
