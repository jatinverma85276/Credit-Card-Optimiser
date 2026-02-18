from app.db.database import engine
from app.db.models import Base, ChatThread

def create_chat_threads_table():
    """Create the chat_threads table"""
    print("Creating chat_threads table...")
    try:
        ChatThread.__table__.create(engine, checkfirst=True)
        print("✅ chat_threads table created successfully!")
        
        # Verify table exists
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"Available tables: {tables}")
        
        if 'chat_threads' in tables:
            print("✅ Verified: chat_threads table exists")
        else:
            print("❌ Warning: chat_threads table not found in database")
            
    except Exception as e:
        print(f"❌ Error creating table: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_chat_threads_table()
