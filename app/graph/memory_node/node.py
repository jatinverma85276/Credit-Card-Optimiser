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

from app.graph.state import GraphState
from dotenv import load_dotenv
from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field
from app.schemas.memory_extraction import MemoryExtraction
from app.services.memory_service import save_general_memory, semantic_search_general_memories
from app.services.memory_service import semantic_search_transactions 
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)

# -------------------------
# Memory Retrieval Node
# -------------------------
def memory_retrieval_node(state: GraphState, config: RunnableConfig):
    # Check if incognito mode
    incognito = config.get("configurable", {}).get("incognito", False)
    
    if incognito:
        print(f"🕵️ Incognito mode: Skipping memory retrieval")
        return {
            **state,
            "memory_context": ""  # Empty context in incognito mode
        }
    
    # Use global user_id for cross-session memory, fallback to thread_id
    user_id = config.get("configurable", {}).get("user_id") or config.get("configurable", {}).get("thread_id")
    last_message = state["messages"][-1].content
    
    print(f"🧠 Retrieving memories for user_id: {user_id}")
    
    # 1. Search Transaction LTM
    relevant_transactions = semantic_search_transactions(
        user_id=user_id, 
        query=last_message, 
        threshold=0.75
    )
    
    # 2. Search General Memories (name, preferences, etc.)
    relevant_general_memories = semantic_search_general_memories(
        user_id=user_id,
        query=last_message,
        threshold=0.25  # Lower threshold for general facts to catch identity queries
    )
    
    # 3. Format Context String
    memory_context = ""
    
    # Add general memories first (identity, preferences)
    if relevant_general_memories:
        memory_context += "### USER PROFILE (Long-term Memory):\n"
        for mem in relevant_general_memories:
            memory_context += f"- {mem.memory_text} [{mem.category}]\n"
        print(f"🧠 LTM: Injecting {len(relevant_general_memories)} general memories.")
    
    # Add transaction memories
    if relevant_transactions:
        memory_context += "\n### RELEVANT PAST TRANSACTIONS:\n"
        for mem in relevant_transactions:
            memory_context += (
                f"- {mem.merchant} ({mem.category}): ₹{mem.amount} "
                f"[Similarity: {mem.similarity:.2f}]\n"
            )
        print(f"🧠 LTM: Injecting {len(relevant_transactions)} transaction memories.")
    
    if not relevant_general_memories and not relevant_transactions:
        print("🧠 LTM: No relevant memories found.")

    # 4. Store in State to be used by the next node
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
    # Check if incognito mode
    incognito = config.get("configurable", {}).get("incognito", False)
    
    if incognito:
        print(f"🕵️ Incognito mode: Skipping profiler (no memory extraction)")
        return state  # Pass through without extracting/saving memories
    
    # Use global user_id for cross-session memory, fallback to thread_id
    user_id = config.get("configurable", {}).get("user_id") or config.get("configurable", {}).get("thread_id", "default")
    print(f"🧠 Profiler checking for memories - user_id: {user_id}")
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