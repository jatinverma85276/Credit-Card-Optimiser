"""
Migration script to add user_auth table for authentication
Run this once to create the authentication table
"""
from sqlalchemy import text
from app.db.database import engine

def migrate():
    with engine.connect() as conn:
        # Create user_auth table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS user_auth (
                id SERIAL PRIMARY KEY,
                user_id VARCHAR UNIQUE NOT NULL,
                email VARCHAR UNIQUE NOT NULL,
                name VARCHAR NOT NULL,
                hashed_password VARCHAR NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """))
        
        # Create index on user_id
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_user_auth_user_id ON user_auth(user_id);
        """))
        
        # Create index on email
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_user_auth_email ON user_auth(email);
        """))
        
        conn.commit()
        print("✅ Migration completed successfully!")
        print("✅ Created user_auth table")
        print("✅ Created indexes on user_id and email")

if __name__ == "__main__":
    migrate()
