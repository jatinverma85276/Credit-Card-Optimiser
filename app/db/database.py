from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 🧠 When we move to Postgres later:
# DATABASE_URL = "postgresql+psycopg2://user:pass@host/db"

DATABASE_URL = "sqlite:///./cards.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # SQLite only
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()
