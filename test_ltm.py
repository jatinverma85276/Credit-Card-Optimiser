from app.services.memory_service import semantic_search_transactions

# 1. Define your User ID (Must match what you used in the graph)
USER_ID = "jatin_1"  # Or whatever thread_id you used

# 2. Search for a CONCEPT (not just a keyword)
query = "buying clothes" 

print(f"🧠 Searching LTM for concept: '{query}'...\n")

# 3. Run the Vector Search
results = semantic_search_transactions(USER_ID, query)

# 4. Print Results
if results:
    print(f"✅ FOUND MATCHES ({len(results)}):")
    for r in results:
        # r is a tuple: (merchant, amount, category, description, similarity)
        # Note: Adjust indices based on your exact SQL query in 'semantic_search_transactions'
        print(f"   - Found: {r.merchant} | ₹{r.amount}")
        print(f"     Context: {r.description}")
        print(f"     Similarity Score: {r.similarity:.4f}")  # Closer to 1.0 is better
        print("-" * 30)
else:
    print("❌ No matching memories found.")