# import sqlite3

# conn = sqlite3.connect("cards.db")
# cursor = conn.cursor()

# cursor.execute("""
#     DELETE FROM credit_cards
#     WHERE rowid = (
#         SELECT MAX(rowid) FROM credit_cards
#     )
# """)

# conn.commit()
# conn.close()

# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker, declarative_base
# from dotenv import load_dotenv
# import os
# from sqlalchemy import text
# from db import engine

# load_dotenv()

# # Database configuration from environment variables
# DB_HOST = os.getenv("DB_HOST", "localhost")
# DB_PORT = os.getenv("DB_PORT", "5432")
# DB_USER = os.getenv("DB_USER", "postgres")
# DB_PASSWORD = os.getenv("DB_PASSWORD", "1234")
# DB_NAME = os.getenv("DB_NAME", "credit_card_ai")

# # 🧠 When we move to Postgres later:
# DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# engine = create_engine(DATABASE_URL)

# with engine.connect() as conn:
#     result = conn.execute(text("SELECT * FROM credit_cards"))
#     rows = result.fetchall()
#     print(rows)
    

import psycopg

conn = psycopg.connect(
    "postgresql://postgres:1234@localhost:5432/credit_card_ai"
)

print("Connected successfully!")
conn.close()
