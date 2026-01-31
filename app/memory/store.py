import sqlite3
from typing import Dict, Any

DB_NAME = "card_agent.db"


class MemoryStore:
    def __init__(self):
        self.conn = sqlite3.connect(DB_NAME)
        self._create_tables()

    def _create_tables(self):
        cursor = self.conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            card_id TEXT,
            amount REAL,
            category TEXT,
            cashback REAL,
            reward_points REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS card_stats (
            card_id TEXT PRIMARY KEY,
            total_spend REAL,
            total_cashback REAL,
            total_reward_points REAL
        )
        """)

        self.conn.commit()

    def get_card_stats(self) -> Dict[str, Any]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM card_stats")
        rows = cursor.fetchall()

        return {
            row[0]: {
                "total_spend": row[1],
                "total_cashback": row[2],
                "total_reward_points": row[3]
            }
            for row in rows
        }

    def record_expense(self, data: Dict[str, Any]):
        cursor = self.conn.cursor()

        cursor.execute("""
        INSERT INTO expenses (card_id, amount, category, cashback, reward_points)
        VALUES (?, ?, ?, ?, ?)
        """, (
            data["card_id"],
            data["amount"],
            data["category"],
            data.get("cashback", 0),
            data.get("reward_points", 0)
        ))

        self.conn.commit()
