from app.db.database import engine
from app.db.models import Base, ChatThread

def create_chat_threads_table():
    """Create the chat_threads table"""
    print("Creating chat_threads table...")
    ChatThread.__table__.create(engine, checkfirst=True)
    print("✅ chat_threads table created successfully!")

if __name__ == "__main__":
    create_chat_threads_table()
