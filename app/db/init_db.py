from app.db.database import engine
from app.db.models import Base
from app.db.models import TransactionHistory

def init_db():
    """Initialize database tables"""
    print("🔧 Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")

if __name__ == "__main__":
    init_db()
