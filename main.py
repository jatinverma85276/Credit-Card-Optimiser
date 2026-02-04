from langchain_core.messages import HumanMessage
from app.graph.graph import build_graph

graph = build_graph()

result = graph.invoke({
    "messages": [
        HumanMessage(content="""I'm thinking to buy a new shirt price is 1400 rupees from nykaa man""")
    ],
    "route": "general"  # default value
})

print(result["messages"][-1].content)
