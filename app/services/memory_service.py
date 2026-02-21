from sqlalchemy import text
from app.db.database import SessionLocal
from app.db.models import TransactionHistory, UserMemory
from app.utils.vectors import get_text_embedding

def save_transaction_memory(user_id: str, merchant: str, amount: float, category: str, desc: str = ""):
    """
    Saves a transaction with its semantic meaning.
    """
    # 1. Create rich context for the vector
    # Combining fields helps the AI understand the *full* context
    semantic_text = f"Merchant: {merchant}, Category: {category}, Description: {desc}"
    
    # 2. Generate Vector
    vector = get_text_embedding(semantic_text)
    
    # 3. Save to DB
    with SessionLocal() as db:
        txn = TransactionHistory(
            user_id=user_id,
            merchant=merchant,
            amount=amount,
            category=category,
            description=desc,
            embedding=vector  # <--- Storing the 'brain'
        )
        db.add(txn)
        db.commit()
        print(f"🧠 Saved memory for: {merchant}")


def semantic_search_transactions(user_id: str, query: str, limit: int = 5, threshold: float = 0.75):
    """
    Finds past transactions that match the user's current query.
    
    Args:
        user_id: The user's thread_id.
        query: The user's current question/intent.
        limit: Max number of memories to retrieve.
        threshold: Minimum similarity score (0 to 1). 
                   0.75 is a good baseline for "strong relevance".
    """
    # 1. Convert User Query to Vector
    query_vector = get_text_embedding(query)
    
    # 2. SQL Query with Threshold Logic
    # We calculate 'similarity' as (1 - cosine_distance)
    # Then we filter WHERE similarity > threshold
    sql = text("""
        WITH calculated_scores AS (
            SELECT 
                merchant, 
                amount, 
                category, 
                description, 
                created_at,
                1 - (embedding <=> :vector) as similarity
            FROM transaction_history
            WHERE user_id = :user_id
        )
        SELECT * FROM calculated_scores
        WHERE similarity >= :threshold
        ORDER BY similarity DESC
        LIMIT :limit;
    """)
    
    with SessionLocal() as db:
        results = db.execute(sql, {
            "user_id": user_id, 
            "vector": str(query_vector), 
            "threshold": threshold,
            "limit": limit
        }).fetchall()
        
    return results


def save_general_memory(user_id: str, text: str, category: str = "general"):
    """
    Saves a non-financial fact about the user.
    """
    # 1. Vectorize the text
    vector = get_text_embedding(text)
    
    # 2. Save to Postgres
    with SessionLocal() as db:
        memory = UserMemory(
            user_id=user_id,
            memory_text=text,
            category=category,
            embedding=vector
        )
        db.add(memory)
        db.commit()
        print(f"🧠 Saved General Memory: '{text}'")


def semantic_search_general_memories(user_id: str, query: str, limit: int = 5, threshold: float = 0.75):
    """
    Finds general user memories (name, preferences, etc.) that match the query.
    
    Args:
        user_id: The user's thread_id.
        query: The user's current question/intent.
        limit: Max number of memories to retrieve.
        threshold: Minimum similarity score (0 to 1).
    """
    # 1. Convert User Query to Vector
    query_vector = get_text_embedding(query)
    
    # 2. SQL Query with Threshold Logic
    sql = text("""
        WITH calculated_scores AS (
            SELECT 
                memory_text, 
                category, 
                created_at,
                1 - (embedding <=> :vector) as similarity
            FROM user_memories
            WHERE user_id = :user_id
        )
        SELECT * FROM calculated_scores
        WHERE similarity >= :threshold
        ORDER BY similarity DESC
        LIMIT :limit;
    """)
    
    with SessionLocal() as db:
        results = db.execute(sql, {
            "user_id": user_id, 
            "vector": str(query_vector), 
            "threshold": threshold,
            "limit": limit
        }).fetchall()
        
    return results