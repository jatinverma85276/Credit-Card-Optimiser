import uuid
from langchain_core.messages import HumanMessage
from app.graph.graph import build_graph
from langgraph.checkpoint.postgres import PostgresSaver
from app.db.database import DATABASE_URL

# graph = build_graph()

# result = graph.invoke({
#     "messages": [
#         HumanMessage(content="""/add_card
# """)
#     ],
#     "route": "general"  # default value
# })

# print(result["messages"][-1].content)

# Build graph (now with memory attached)


def run_cli(graph):
    print("\n💳 Credit Card Optimiser Agent (with Memory)")
    print("Type 'exit' to quit.\n")

    # 1. Generate a Thread ID for this session
    # In a web app, this would be the user_id or session_id
    thread_id = str(uuid.uuid4())
    
    # 2. Config dictionary tells the graph which memory to load
    # config = {"configurable": {"thread_id": thread_id}}
    config = {"configurable": {"thread_id": "jatin_1"}}

    while True:
        user_input = input("You: ")

        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye 👋")
            break

        # 3. STREAMING OUTPUT
        # We only pass the NEW message. The graph loads the rest from DB.
        inputs = {"messages": [HumanMessage(content=user_input)]}
        
        # Pass 'config' so it knows which thread to update
        for event in graph.stream(inputs, config=config):
            for key, value in event.items():
                # Optional: Print intermediate steps if you want to debug
                # print(f"  -> Processed by: {key}")
                pass
        
        # 4. Fetch the final state to get the bot's response
        # 'graph.get_state(config)' gets the current snapshot of memory
        snapshot = graph.get_state(config)
        
        if snapshot.values and "messages" in snapshot.values:
            last_msg = snapshot.values["messages"][-1]
            print(f"\nAgent: {last_msg.content}\n")
        else:
            print("\nAgent: ... (No response)\n")

# if __name__ == "__main__":
#     run_cli()

print(DATABASE_URL,"DATABASE_URL")
with PostgresSaver.from_conn_string(DATABASE_URL) as memory:
    # memory.setup()
    graph = build_graph(memory)
    run_cli(graph)

# graph = build_graph()
