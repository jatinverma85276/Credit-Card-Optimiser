import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from app.graph.graph import build_graph
from langgraph.checkpoint.postgres import PostgresSaver
from app.db.database import DATABASE_URL, engine
from sqlalchemy import text

# Global graph instance
graph = None
memory = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown"""
    global graph, memory
    # Startup
    memory = PostgresSaver.from_conn_string(DATABASE_URL)
    memory.__enter__()  # Enter the context manager
    graph = build_graph(memory)
    yield
    # Shutdown
    if memory:
        memory.__exit__(None, None, None)  # Exit the context manager

app = FastAPI(title="Credit Card Optimizer API", lifespan=lifespan)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    thread_id: str = None

class ChatResponse(BaseModel):
    response: str
    thread_id: str

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):  
    """
    Chat endpoint for interacting with the credit card optimizer agent
    """
    if not graph:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    # Generate or use provided thread_id
    thread_id = request.thread_id or str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    try:
        # Process message through graph
        inputs = {"messages": [HumanMessage(content=request.message)]}
        
        for event in graph.stream(inputs, config=config):
            pass  # Process all events
        
        # Get final response
        snapshot = graph.get_state(config)
        
        if snapshot.values and "messages" in snapshot.values:
            last_msg = snapshot.values["messages"][-1]
            response_text = last_msg.content
        else:
            response_text = "No response generated"
        
        return ChatResponse(response=response_text, thread_id=thread_id)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")

@app.get("/health")
async def health_check():
    """
    Health check endpoint - verifies server and database connectivity
    """
    health_status = {
        "status": "healthy",
        "database": "disconnected",
        "graph": "not_initialized"
    }
    
    # Check database connection
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        health_status["database"] = "connected"
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["database"] = f"error: {str(e)}"
    
    # Check graph initialization
    if graph:
        health_status["graph"] = "initialized"
    else:
        health_status["status"] = "unhealthy"
    
    if health_status["status"] != "healthy":
        raise HTTPException(status_code=503, detail=health_status)
    
    return health_status
