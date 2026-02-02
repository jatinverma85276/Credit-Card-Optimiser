import sqlite3

conn = sqlite3.connect("cards.db")  # adjust path if needed
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
cursor.execute("SELECT * FROM credit_cards")
tables = cursor.fetchall()

print("Tables found:", tables)

conn.close()
