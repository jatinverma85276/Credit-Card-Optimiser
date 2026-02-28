from app.db.database import engine
from app.db.models import Base
from app.db.models import TransactionHistory
from sqlalchemy import text

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
    
    print("🔧 Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")

if __name__ == "__main__":
    init_db()
