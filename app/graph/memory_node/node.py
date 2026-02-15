from app.graph.state import GraphState
from dotenv import load_dotenv
from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field
from app.schemas.memory_extraction import MemoryExtraction
from app.services.memory_service import save_general_memory
from app.services.memory_service import semantic_search_transactions 
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)

# -------------------------
# Memory Retrieval Node
# -------------------------
def memory_retrieval_node(state: GraphState, config: RunnableConfig):
    user_id = config.get("configurable", {}).get("thread_id")
    last_message = state["messages"][-1].content
    
    # 1. Search LTM with strict threshold
    # This will return EMPTY list if nothing is relevant (> 0.75)
    relevant_memories = semantic_search_transactions(
        user_id=user_id, 
        query=last_message, 
        threshold=0.75
    )
    
    # 2. Format Context String (Only if data found)
    memory_context = ""
    if relevant_memories:
        memory_context = "### RELEVANT PAST TRANSACTIONS (LTM):\n"
        for mem in relevant_memories:
            # mem is a Row object: (merchant, amount, category, description, created_at, similarity)
            memory_context += (
                f"- {mem.merchant} ({mem.category}): ₹{mem.amount} "
                f"[Similarity: {mem.similarity:.2f}]\n"
            )
        print(f"🧠 LTM Injecting {len(relevant_memories)} memories.")
    else:
        print("🧠 LTM: No relevant memories found.")

    # 3. Store in State to be used by the next node
    return {
        **state,
        "memory_context": memory_context 
    }


PROFILER_SYSTEM_PROMPT = """
You are a Memory Agent. 
Your ONLY job is to extract permanent facts about the user.

Examples:
- User: "My name is Jatin" -> Fact: "User's name is Jatin" (identity)
- User: "I love Italian food" -> Fact: "User loves Italian food" (preference)
- User: "Hi how are you?" -> Fact: None (Ignore)

Return valid JSON.
"""

def profiler_node(state: GraphState, config: RunnableConfig):
    user_id = config.get("configurable", {}).get("thread_id", "default")
    print(user_id, "user_id")
    last_msg = state["messages"][-1].content
    
    # 1. Run LLM to see if there is a fact
    extractor = llm.with_structured_output(MemoryExtraction)
    result = extractor.invoke([
        SystemMessage(content=PROFILER_SYSTEM_PROMPT),
        last_msg
    ])
    
    # 2. Save if a fact was found
    if result.important_fact:
        save_general_memory(
            user_id=user_id,
            text=result.important_fact,
            category=result.category
        )
        
    # Pass state through (don't stop the flow)
    return state