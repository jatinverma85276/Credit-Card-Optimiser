from app.db.database import engine
from app.db.models import Base
from app.db.models import TransactionHistory

def init_db():
    Base.metadata.create_all(bind=engine)
