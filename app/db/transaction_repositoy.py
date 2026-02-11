import psycopg2
from app.db.database import DATABASE_URL


def save_transaction(data):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO transactions (
            user_id,
            merchant,
            category,
            amount,
            recommended_card,
            reward_points
        )
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        data["user_id"],
        data.get("merchant"),
        data.get("category"),
        data.get("amount"),
        data.get("recommended_card"),
        data.get("reward_points")
    ))

    conn.commit()
    cur.close()
    conn.close()
