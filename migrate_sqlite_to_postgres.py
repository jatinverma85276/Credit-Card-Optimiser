import sqlite3
import psycopg2
import json

# Connect SQLite
sqlite_conn = sqlite3.connect("cards.db")
sqlite_cursor = sqlite_conn.cursor()

# Connect Postgres
pg_conn = psycopg2.connect(
    dbname="credit_card_ai",
    user="postgres",
    password="1234",
    host="localhost",
    port="5432"
)

pg_cursor = pg_conn.cursor()

# ---- Create Table (Run Once) ----
pg_cursor.execute("""
CREATE TABLE IF NOT EXISTS credit_cards (
    id SERIAL PRIMARY KEY,
    card_name TEXT UNIQUE,
    issuer TEXT,
    card_type TEXT,
    annual_fee TEXT,
    fee_waiver_condition TEXT,
    welcome_bonus TEXT,
    reward_program_name TEXT,
    reward_rules JSONB,
    milestone_benefits JSONB,
    eligibility_criteria JSONB,
    excluded_categories JSONB,
    key_benefits JSONB,
    liability_policy TEXT
);
""")

pg_conn.commit()

# ---- Fetch SQLite Data ----
sqlite_cursor.execute("SELECT * FROM credit_cards")
rows = sqlite_cursor.fetchall()

columns = [desc[0] for desc in sqlite_cursor.description]

for row in rows:
    data = dict(zip(columns, row))

    # Convert JSON strings safely
    for field in [
        "reward_rules",
        "milestone_benefits",
        "eligibility_criteria",
        "excluded_categories",
        "key_benefits"
    ]:
        if data.get(field):
            if isinstance(data[field], str):
                data[field] = json.loads(data[field])

    pg_cursor.execute("""
        INSERT INTO credit_cards (
            card_name, issuer, card_type, annual_fee,
            fee_waiver_condition, welcome_bonus,
            reward_program_name, reward_rules,
            milestone_benefits, eligibility_criteria,
            excluded_categories, key_benefits,
            liability_policy
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (card_name) DO NOTHING;
    """, (
        data["card_name"],
        data["issuer"],
        data["card_type"],
        data["annual_fee"],
        data["fee_waiver_condition"],
        data["welcome_bonus"],
        data["reward_program_name"],
        json.dumps(data["reward_rules"]),
        json.dumps(data["milestone_benefits"]),
        json.dumps(data["eligibility_criteria"]),
        json.dumps(data["excluded_categories"]),
        json.dumps(data["key_benefits"]),
        data["liability_policy"]
    ))

pg_conn.commit()

print("✅ Migration Completed Successfully!")

sqlite_conn.close()
pg_conn.close()
