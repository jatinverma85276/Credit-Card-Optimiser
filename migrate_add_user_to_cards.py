"""
Migration script to add user_id to credit_cards table
Run this once to update your database schema
"""
from sqlalchemy import text
from app.db.database import engine

def migrate():
    with engine.connect() as conn:
        # Add user_id column to credit_cards if it doesn't exist
        conn.execute(text("""
            DO $$ 
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='credit_cards' AND column_name='user_id'
                ) THEN
                    ALTER TABLE credit_cards ADD COLUMN user_id VARCHAR;
                END IF;
            END $$;
        """))
        
        # Create index on credit_cards.user_id
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_credit_cards_user_id ON credit_cards(user_id);
        """))
        
        # Drop the unique constraint on card_name (multiple users can have same card)
        conn.execute(text("""
            DO $$ 
            BEGIN
                IF EXISTS (
                    SELECT 1 FROM pg_constraint 
                    WHERE conname = 'credit_cards_card_name_key'
                ) THEN
                    ALTER TABLE credit_cards DROP CONSTRAINT credit_cards_card_name_key;
                END IF;
            END $$;
        """))
        
        # Update existing cards to have a default user_id (optional)
        conn.execute(text("""
            UPDATE credit_cards 
            SET user_id = 'default_user' 
            WHERE user_id IS NULL;
        """))
        
        conn.commit()
        print("✅ Migration completed successfully!")
        print("✅ Added user_id to credit_cards table")
        print("✅ Removed unique constraint on card_name")
        print("✅ Updated existing cards with default_user")

if __name__ == "__main__":
    migrate()
