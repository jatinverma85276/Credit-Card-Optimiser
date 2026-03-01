from app.db.database import engine, DATABASE_URL
from app.db.models import Base
from app.db.models import TransactionHistory
from sqlalchemy import text
from langgraph.checkpoint.postgres import PostgresSaver

def init_db():
    """Initialize database tables"""
    print("🔧 Enabling pgvector extension...")
    
    # Enable pgvector extension
    with engine.connect() as conn:
        try:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            conn.commit()
            print("✅ pgvector extension enabled!")
        except Exception as e:
            print(f"⚠️  Warning: Could not enable pgvector extension: {e}")
            print("   Continuing anyway...")
    
    print("🔧 Creating application database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Application tables created successfully!")
    
    print("🔧 Creating LangGraph checkpoint tables...")
    try:
        # Initialize PostgresSaver to create checkpoint tables
        with PostgresSaver.from_conn_string(DATABASE_URL) as checkpointer:
            # The context manager automatically sets up the tables
            print("✅ LangGraph checkpoint tables created successfully!")
    except Exception as e:
        print(f"⚠️  Warning: Could not create checkpoint tables: {e}")
        print("   Continuing anyway...")

if __name__ == "__main__":
    init_db()
