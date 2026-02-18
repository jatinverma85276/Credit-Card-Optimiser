import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from app.graph.graph import build_graph
from langgraph.checkpoint.postgres import PostgresSaver
from app.db.database import DATABASE_URL, engine, SessionLocal
from app.db.models import ChatThread
from sqlalchemy import text

# Global graph instance
graph = None
memory = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown"""
    global graph, memory
    # Startup
    memory_context = PostgresSaver.from_conn_string(DATABASE_URL)
    memory = memory_context.__enter__()  # Get the actual saver instance
    graph = build_graph(memory)
    yield
    # Shutdown
    if memory_context:
        memory_context.__exit__(None, None, None)  # Exit the context manager

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

class Message(BaseModel):
    role: str
    content: str

class ChatHistoryResponse(BaseModel):
    thread_id: str
    messages: list[Message]

class ThreadListResponse(BaseModel):
    threads: list[str]
    count: int

class ThreadInfo(BaseModel):
    thread_id: str
    thread_name: str
    created_at: str
    updated_at: str

class ThreadListDetailedResponse(BaseModel):
    threads: list[ThreadInfo]
    count: int

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):  
    """
    Chat endpoint for interacting with the credit card optimizer agent
    """
    if not graph:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    # Generate or use provided thread_id
    is_new_thread = request.thread_id is None
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
        
        # Save thread name if it's a new thread
        if is_new_thread:
            db = SessionLocal()
            try:
                # Create thread name from first 50 chars of message
                thread_name = request.message[:50] + "..." if len(request.message) > 50 else request.message
                
                new_thread = ChatThread(
                    thread_id=thread_id,
                    thread_name=thread_name
                )
                db.add(new_thread)
                db.commit()
            except Exception as e:
                db.rollback()
                print(f"Error saving thread metadata: {str(e)}")
            finally:
                db.close()
        
        return ChatResponse(response=response_text, thread_id=thread_id)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")

@app.get("/chat/threads", response_model=ThreadListDetailedResponse)
async def get_all_threads():
    """
    Get all thread IDs (session IDs) with their names from the database
    """
    if not graph:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        db = SessionLocal()
        try:
            threads = db.query(ChatThread).order_by(ChatThread.updated_at.desc()).all()
            
            thread_list = [
                ThreadInfo(
                    thread_id=thread.thread_id,
                    thread_name=thread.thread_name,
                    created_at=thread.created_at.isoformat(),
                    updated_at=thread.updated_at.isoformat()
                )
                for thread in threads
            ]
            
            return ThreadListDetailedResponse(threads=thread_list, count=len(thread_list))
        finally:
            db.close()
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving threads: {str(e)}")

@app.get("/chat/history/{thread_id}", response_model=ChatHistoryResponse)
async def get_chat_history(thread_id: str):
    """
    Get chat history for a specific thread
    """
    if not graph:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        config = {"configurable": {"thread_id": thread_id}}
        snapshot = graph.get_state(config)
        
        if not snapshot.values or "messages" not in snapshot.values:
            raise HTTPException(status_code=404, detail="Thread not found or no messages")
        
        messages = []
        for msg in snapshot.values["messages"]:
            # Determine role based on message type
            role = "user" if msg.__class__.__name__ == "HumanMessage" else "assistant"
            messages.append(Message(role=role, content=msg.content))
        
        return ChatHistoryResponse(thread_id=thread_id, messages=messages)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving chat history: {str(e)}")

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
