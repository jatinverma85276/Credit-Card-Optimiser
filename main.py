import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, AIMessage
from app.graph.graph import build_graph
from langgraph.checkpoint.postgres import PostgresSaver
from app.db.database import DATABASE_URL, engine, SessionLocal
from app.db.models import ChatThread, User
from sqlalchemy import text
import json

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

class UserInfo(BaseModel):
    id: str
    name: str
    email: str

class ChatRequest(BaseModel):
    message: str
    thread_id: str = None
    user: UserInfo  # Required user information
    stream: bool = False

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

class UserResponse(BaseModel):
    user_id: str
    name: str
    email: str
    created_at: str
    updated_at: str

@app.post("/chat")
async def chat(request: ChatRequest):  
    """
    Chat endpoint for interacting with the credit card optimizer agent
    Supports streaming with stream=true parameter
    user: User information (id, name, email) - used for LTM and personalization
    thread_id: Session-specific conversation thread
    """
    if not graph:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    # Generate or use provided thread_id
    thread_id = request.thread_id if request.thread_id else str(uuid.uuid4())
    
    # Save or update user information
    db = SessionLocal()
    try:
        # Check if user exists
        existing_user = db.query(User).filter(User.user_id == request.user.id).first()
        if not existing_user:
            # Create new user
            new_user = User(
                user_id=request.user.id,
                name=request.user.name,
                email=request.user.email
            )
            db.add(new_user)
            db.commit()
            print(f"✅ Created new user: {request.user.name} ({request.user.email})")
        else:
            # Update user info if changed
            if existing_user.name != request.user.name or existing_user.email != request.user.email:
                existing_user.name = request.user.name
                existing_user.email = request.user.email
                db.commit()
                print(f"✅ Updated user info: {request.user.name}")
    except Exception as e:
        db.rollback()
        print(f"❌ Error saving user: {str(e)}")
    finally:
        db.close()
    
    # Config with both thread_id (for conversation) and user_id (for LTM)
    config = {
        "configurable": {
            "thread_id": thread_id,
            "user_id": request.user.id  # Use actual user ID for cross-session memory
        }
    }
    
    # Save thread metadata if it's a new thread
    if request.thread_id:
        db = SessionLocal()
        try:
            # Check if thread already exists
            existing_thread = db.query(ChatThread).filter(ChatThread.thread_id == thread_id).first()
            if not existing_thread:
                thread_name = request.message[:50] + "..." if len(request.message) > 50 else request.message
                new_thread = ChatThread(
                    thread_id=thread_id,
                    user_id=request.user.id,
                    thread_name=thread_name
                )
                db.add(new_thread)
                db.commit()
                db.refresh(new_thread)
                print(f"✅ Saved new thread: {thread_id} - {thread_name}")
            else:
                print(f"Thread {thread_id} already exists")
        except Exception as e:
            db.rollback()
            print(f"❌ Error saving thread metadata: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            db.close()
    
    try:
        # Process message through graph
        inputs = {"messages": [HumanMessage(content=request.message)]}
        
        if request.stream:
            # Streaming response
            async def event_generator():
                try:
                    for event in graph.stream(inputs, config=config):
                        # Stream intermediate steps
                        for node_name, node_data in event.items():
                            if "messages" in node_data and node_data["messages"]:
                                last_msg = node_data["messages"][-1]
                                if isinstance(last_msg, AIMessage):
                                    yield f"data: {json.dumps({'type': 'progress', 'node': node_name, 'content': last_msg.content})}\n\n"
                    
                    # Get final response
                    snapshot = graph.get_state(config)
                    if snapshot.values and "messages" in snapshot.values:
                        last_msg = snapshot.values["messages"][-1]
                        response_text = last_msg.content
                    else:
                        response_text = "No response generated"
                    
                    # Send final response
                    yield f"data: {json.dumps({'type': 'final', 'response': response_text, 'thread_id': thread_id})}\n\n"
                    
                except Exception as e:
                    yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
            
            return StreamingResponse(event_generator(), media_type="text/event-stream")
        
        else:
            # Non-streaming response (original behavior)
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

@app.get("/user/{user_id}/threads", response_model=ThreadListDetailedResponse)
async def get_user_thread_ids(user_id: str):
    """
    Get all threads for a specific user with detailed information
    """
    if not graph:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        db = SessionLocal()
        try:
            threads = db.query(ChatThread).filter(
                ChatThread.user_id == user_id
            ).order_by(ChatThread.updated_at.desc()).all()
            
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

@app.get("/user/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    """
    Get user information by user_id
    """
    try:
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.user_id == user_id).first()
            if not user:
                raise HTTPException(status_code=404, detail=f"User {user_id} not found")
            
            return UserResponse(
                user_id=user.user_id,
                name=user.name,
                email=user.email,
                created_at=user.created_at.isoformat(),
                updated_at=user.updated_at.isoformat()
            )
        finally:
            db.close()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving user: {str(e)}")

@app.get("/chat/threads", response_model=ThreadListDetailedResponse)
async def get_all_threads(user_id: str = None):
    """
    Get all thread IDs (session IDs) with their names from the database
    Optionally filter by user_id
    """
    if not graph:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        db = SessionLocal()
        try:
            query = db.query(ChatThread)
            if user_id:
                query = query.filter(ChatThread.user_id == user_id)
            
            threads = query.order_by(ChatThread.updated_at.desc()).all()
            
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
    Get chat history for a specific thread (only user messages and final assistant responses)
    """
    if not graph:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        config = {"configurable": {"thread_id": thread_id}}
        snapshot = graph.get_state(config)
        
        if not snapshot.values or "messages" not in snapshot.values:
            raise HTTPException(status_code=404, detail="Thread not found or no messages")
        
        messages = []
        all_messages = snapshot.values["messages"]
        
        # Filter to show only user messages and final assistant responses
        for i, msg in enumerate(all_messages):
            if msg.__class__.__name__ == "HumanMessage":
                # Always include user messages
                messages.append(Message(role="user", content=msg.content))
            elif msg.__class__.__name__ == "AIMessage":
                # Only include the last AI message before the next user message or end
                is_last_ai = (i == len(all_messages) - 1) or (i + 1 < len(all_messages) and all_messages[i + 1].__class__.__name__ == "HumanMessage")
                if is_last_ai:
                    messages.append(Message(role="assistant", content=msg.content))
        
        return ChatHistoryResponse(thread_id=thread_id, messages=messages)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving chat history: {str(e)}")

@app.delete("/chat/thread/{thread_id}")
async def delete_thread(thread_id: str):
    """
    Delete a specific thread/session including:
    - Thread metadata from chat_threads table
    - Conversation history from checkpoints
    """
    if not graph or not memory:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        db = SessionLocal()
        deleted_items = {
            "thread_metadata": False,
            "checkpoints": False
        }
        
        try:
            # Delete thread metadata from chat_threads table
            thread = db.query(ChatThread).filter(ChatThread.thread_id == thread_id).first()
            if thread:
                db.delete(thread)
                db.commit()
                deleted_items["thread_metadata"] = True
            
            # Delete checkpoints from PostgresSaver
            # The checkpoints table stores conversation history
            with engine.connect() as conn:
                # Delete from checkpoints table
                result = conn.execute(
                    text("DELETE FROM checkpoints WHERE thread_id = :thread_id"),
                    {"thread_id": thread_id}
                )
                conn.commit()
                
                if result.rowcount > 0:
                    deleted_items["checkpoints"] = True
            
            if not deleted_items["thread_metadata"] and not deleted_items["checkpoints"]:
                raise HTTPException(status_code=404, detail=f"Thread {thread_id} not found")
            
            return {
                "message": f"Thread {thread_id} deleted successfully",
                "thread_id": thread_id,
                "deleted": deleted_items
            }
        
        finally:
            db.close()
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting thread: {str(e)}")

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
