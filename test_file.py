import sqlite3

conn = sqlite3.connect("cards.db")
cursor = conn.cursor()

cursor.execute("""
    DELETE FROM credit_cards
    WHERE rowid = (
        SELECT MAX(rowid) FROM credit_cards
    )
""")

conn.commit()
conn.close()
