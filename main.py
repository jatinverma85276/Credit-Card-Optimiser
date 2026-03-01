import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, EmailStr
from langchain_core.messages import HumanMessage, AIMessage
from app.graph.graph import build_graph
from langgraph.checkpoint.postgres import PostgresSaver
from app.db.database import DATABASE_URL, engine, SessionLocal
from app.db.models import ChatThread, UserAuth
from app.services.auth_service import create_user, authenticate_user
from app.db.card_repository import get_user_cards
from app.schemas.credit_card import CreditCard, RewardRule, Milestone, Eligibility
from sqlalchemy import text
import json
from typing import List
from app.graph.nodes import llm  # Import LLM for card parsing

# Global graph instances
graph = None  # Graph with memory (normal mode)
graph_incognito = None  # Graph without memory (incognito mode)
memory = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown"""
    global graph, graph_incognito, memory
    
    # Startup
    print("🚀 Starting Credit Card Optimizer API...")
    
    # Initialize PostgresSaver - this creates checkpoint tables if they don't exist
    print("🔧 Initializing checkpoint storage...")
    memory_context = PostgresSaver.from_conn_string(DATABASE_URL)
    memory = memory_context.__enter__()  # Get the actual saver instance
    
    # Force checkpoint table creation by calling setup
    try:
        print("🔧 Setting up checkpoint tables...")
        memory.setup()
        print("✅ Checkpoint tables created/verified!")
    except Exception as e:
        print(f"⚠️  Warning during checkpoint setup: {e}")
    
    print("✅ Checkpoint storage initialized!")
    
    # Build graph with memory for normal mode
    print("🔧 Building graph with memory...")
    graph = build_graph(memory)
    
    # Build graph without memory for incognito mode
    print("🔧 Building incognito graph...")
    graph_incognito = build_graph(None)
    
    print("✅ API ready to serve requests!")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down...")
    if memory_context:
        memory_context.__exit__(None, None, None)  # Exit the context manager
    print("✅ Shutdown complete!")

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
    incognito: bool = False  # Incognito mode - no data saved

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

class SignupRequest(BaseModel):
    name: str
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class AuthResponse(BaseModel):
    user_id: str
    name: str
    email: str
    message: str

class CardResponse(BaseModel):
    id: int
    card_name: str
    issuer: str
    card_type: str
    annual_fee: str
    fee_waiver_condition: str | None
    welcome_bonus: str | None
    liability_policy: str | None
    reward_program_name: str | None
    reward_rules: List[dict]
    milestone_benefits: List[dict]
    eligibility_criteria: dict | None
    excluded_categories: List[str]
    key_benefits: List[str]

class UserCardsResponse(BaseModel):
    user_id: str
    cards: List[CardResponse]
    count: int

@app.post("/auth/signup", response_model=AuthResponse)
async def signup(request: SignupRequest):
    """
    User signup endpoint
    Creates a new user account with hashed password
    """
    db = SessionLocal()
    try:
        # Create user in auth table
        user = create_user(db, request.email, request.name, request.password)
        
        return AuthResponse(
            user_id=user.user_id,
            name=user.name,
            email=user.email,
            message="Account created successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        print(f"❌ Signup error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error creating account: {str(e)}")
    finally:
        db.close()

@app.post("/auth/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """
    User login endpoint
    Authenticates user with email and password
    """
    db = SessionLocal()
    try:
        # Authenticate user
        user = authenticate_user(db, request.email, request.password)
        
        if not user:
            raise HTTPException(
                status_code=401, 
                detail="Invalid email or password"
            )
        
        return AuthResponse(
            user_id=user.user_id,
            name=user.name,
            email=user.email,
            message="Login successful"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during login: {str(e)}")
    finally:
        db.close()

@app.post("/chat")
async def chat(request: ChatRequest):  
    """
    Chat endpoint for interacting with the credit card optimizer agent
    
    Parameters:
    - message: User's message
    - user: User information (id, name, email)
    - thread_id: Session-specific conversation thread (optional)
    - stream: Enable streaming response (optional)
    - incognito: Incognito mode - no conversation or transaction data saved (optional)
    
    Incognito Mode:
    - When incognito=true, no data is saved:
      - No conversation history saved
      - No transaction memory saved
      - No thread metadata saved
    - User can still get recommendations based on their registered cards
    - Useful for privacy-sensitive queries
    """
    if not graph or not graph_incognito:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    # Select the appropriate graph based on incognito mode
    active_graph = graph_incognito if request.incognito else graph
    
    # Generate or use provided thread_id
    # In incognito mode, use a temporary thread_id that won't be saved
    if request.incognito:
        thread_id = f"incognito_{uuid.uuid4()}"
    else:
        thread_id = request.thread_id if request.thread_id else str(uuid.uuid4())
    
    # Save or update user information (unless incognito)
    if not request.incognito:
        db = SessionLocal()
        try:
            # Check if user exists by user_id OR email
            existing_user = db.query(UserAuth).filter(
                (UserAuth.user_id == request.user.id) | (UserAuth.email == request.user.email)
            ).first()
            
            if not existing_user:
                # User should already exist from signup, but log if not found
                print(f"⚠️ User not found in user_auth: {request.user.id} ({request.user.email})")
            else:
                # Update user info if changed
                if existing_user.name != request.user.name:
                    existing_user.name = request.user.name
                    db.commit()
                    print(f"✅ Updated user info: {request.user.name}")
        except Exception as e:
            db.rollback()
            print(f"❌ Error updating user: {str(e)}")
        finally:
            db.close()
    
    # Config with both thread_id (for conversation) and user_id (for LTM)
    # Add incognito flag to config so nodes can check it
    config = {
        "configurable": {
            "thread_id": thread_id,
            "user_id": request.user.id,
            "incognito": request.incognito  # Pass incognito mode to nodes
        }
    }
    
    # Save thread metadata if it's a new thread (skip in incognito mode)
    if request.thread_id and not request.incognito:
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
    elif request.incognito:
        print(f"🕵️ Incognito mode: No thread metadata saved for {thread_id}")
    
    try:
        # Process message through graph
        inputs = {"messages": [HumanMessage(content=request.message)]}
        
        if request.stream:
            # Streaming response
            async def event_generator():
                try:
                    for event in active_graph.stream(inputs, config=config):
                        # Stream intermediate steps
                        for node_name, node_data in event.items():
                            if "messages" in node_data and node_data["messages"]:
                                last_msg = node_data["messages"][-1]
                                if isinstance(last_msg, AIMessage):
                                    yield f"data: {json.dumps({'type': 'progress', 'node': node_name, 'content': last_msg.content})}\n\n"
                    
                    # Get final response
                    if request.incognito:
                        # In incognito mode, we can't use get_state, so we already have the response from stream
                        response_text = last_msg.content if last_msg else "No response generated"
                    else:
                        # Normal mode: use get_state
                        snapshot = active_graph.get_state(config)
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
            final_state = None
            for event in active_graph.stream(inputs, config=config):
                # Keep track of the last state
                final_state = event
            
            # Get final response
            # In incognito mode (no checkpointer), get_state won't work, so use final_state from stream
            if request.incognito and final_state:
                # Extract response from final state
                for node_name, node_data in final_state.items():
                    if "messages" in node_data and node_data["messages"]:
                        last_msg = node_data["messages"][-1]
                        response_text = last_msg.content
                        break
                else:
                    response_text = "No response generated"
            else:
                # Normal mode: use get_state
                snapshot = active_graph.get_state(config)
                
                if snapshot.values and "messages" in snapshot.values:
                    last_msg = snapshot.values["messages"][-1]
                    response_text = last_msg.content
                else:
                    response_text = "No response generated"
            
            return ChatResponse(response=response_text, thread_id=thread_id)
    
    except Exception as e:
        import traceback
        traceback.print_exc()
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
            user = db.query(UserAuth).filter(UserAuth.user_id == user_id).first()
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

@app.get("/user/{user_id}/cards", response_model=UserCardsResponse)
async def get_user_cards_endpoint(user_id: str):
    """
    Get all credit cards for a specific user
    """
    try:
        db = SessionLocal()
        try:
            # Fetch cards from database
            cards = get_user_cards(db, user_id)
            
            # Convert to response format
            card_responses = [
                CardResponse(
                    id=card.id,
                    card_name=card.card_name,
                    issuer=card.issuer,
                    card_type=card.card_type,
                    annual_fee=card.annual_fee,
                    fee_waiver_condition=card.fee_waiver_condition,
                    welcome_bonus=card.welcome_bonus,
                    liability_policy=card.liability_policy,
                    reward_program_name=card.reward_program_name,
                    reward_rules=card.reward_rules or [],
                    milestone_benefits=card.milestone_benefits or [],
                    eligibility_criteria=card.eligibility_criteria,
                    excluded_categories=card.excluded_categories or [],
                    key_benefits=card.key_benefits or []
                )
                for card in cards
            ]
            
            return UserCardsResponse(
                user_id=user_id,
                cards=card_responses,
                count=len(card_responses)
            )
        finally:
            db.close()
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error retrieving cards: {str(e)}")

class AddCardRequest(BaseModel):
    bank_name: str
    card_name: str
    user_id: str

class AddCardResponse(BaseModel):
    success: bool
    message: str
    card_details: dict | None = None

@app.post("/add_card", response_model=AddCardResponse)
async def add_card_endpoint(request: AddCardRequest):
    """
    Add a credit card by searching for its details online
    
    Parameters:
    - bank_name: Name of the bank/issuer (e.g., "HDFC", "ICICI", "American Express")
    - card_name: Name of the card (e.g., "Regalia Gold", "Amazon Pay", "Platinum Travel")
    - user_id: User ID to associate the card with
    
    This endpoint will:
    1. Search for card details online using web search
    2. Parse and extract structured card information
    3. Save the card to the database
    """
    try:
        from app.tools.web_search import search_product_price
        from langchain_core.messages import SystemMessage
        
        # Step 1: Search for card details online
        search_query = f"{request.bank_name} {request.card_name} credit card features benefits rewards India"
        print(f"🔍 Searching for: {search_query}")
        
        search_results = search_product_price.invoke({"product_name": search_query})
        
        if not search_results or "Error" in search_results:
            raise HTTPException(
                status_code=404, 
                detail=f"Could not find details for {request.bank_name} {request.card_name}. Please try with more specific card name or add details manually."
            )
        
        print(f"✅ Found search results (length: {len(search_results)})")
        
        # Step 2: Parse the card details using the card parser
        structured_llm = llm.with_structured_output(CreditCard)
        
        CARD_EXTRACTION_PROMPT = """
You are a STRICT Financial Data Extractor. Your goal is to map unstructured text to a structured schema with 100% fidelity to the source text.

### CORE PHILOSOPHY:
1. **NO INFERENCE:** If the user says "5% on travel", extract exactly that. Do NOT infer "Foreign Transaction Fee Waiver" unless explicitly stated.
2. **NO AUTOFILL:** Do not fill in generic data (like "18 years old" or "Indian Resident") unless the text explicitly mentions these criteria.
3. **NO GUESSING:** If a field (like `annual_fee`) is missing from the text, return `null`. Do not guess based on similar cards.

### DATA HANDLING RULES:
1. **Analyze Footnotes:** Critical data (caps, specific exclusions) is often hidden in footnotes (e.g., "1", "2"). You MUST integrate this data into the main fields.
2. **Split Reward Buckets:** If a single category (like "10X Rewards") has different caps for different merchant groups (e.g., "Group A capped at 500, Group B capped at 500"), create **separate** `RewardRule` entries.
3. **Capture Eligibility:** Extract income, age, and location constraints into `eligibility_criteria` ONLY if explicitly mentioned.
4. **Milestones:** Map "Spend X to get Y" logic to `milestone_benefits`.
5. **Exclusions:** Be specific. If EMI is excluded only at "Point of Sale", record that nuance.

### VALIDATION & FAILURE HANDLING:
- **`extracted_from_user` Flag:** Set to `true` IF the text contains specific, identifiable credit card terms (e.g., specific reward rates, fee amounts, or unique benefit names).
  Set to `false` IF the input is vague, generic, or lacks sufficient detail to identify a specific financial product.

### OUTPUT FORMAT:
Return strictly valid JSON matching the provided schema.
"""
        
        card_data: CreditCard = structured_llm.invoke([
            SystemMessage(content=CARD_EXTRACTION_PROMPT),
            f"Extract credit card details from this search result:\n\n{search_results}"
        ])
        
        if not card_data.extracted_from_user:
            raise HTTPException(
                status_code=422,
                detail=f"Could not extract valid card details from search results. The information found was too generic or incomplete. Please try adding the card manually with full details."
            )
        
        print(f"✅ Parsed card: {card_data.card_name}")
        
        # Step 3: Save to database
        db = SessionLocal()
        try:
            from app.db.card_repository import add_card
            db_card = add_card(db, card_data, request.user_id)
            
            # Convert to dict for response
            card_dict = {
                "id": db_card.id,
                "card_name": db_card.card_name,
                "issuer": db_card.issuer,
                "card_type": db_card.card_type,
                "annual_fee": db_card.annual_fee,
                "reward_program_name": db_card.reward_program_name,
                "reward_rules": db_card.reward_rules,
                "key_benefits": db_card.key_benefits
            }
            
            return AddCardResponse(
                success=True,
                message=f"Successfully added {card_data.card_name} to your portfolio",
                card_details=card_dict
            )
        finally:
            db.close()
    
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500, 
            detail=f"Error adding card: {str(e)}"
        )

@app.get("/health")
async def health_check():
    """
    Health check endpoint - verifies server and database connectivity
    """
    health_status = {
        "status": "healthy",
        "database": "disconnected",
        "graph": "not_initialized",
        "checkpoint_tables": "unknown"
    }
    
    # Check database connection and checkpoint tables
    try:
        with engine.connect() as conn:
            # Test basic connectivity
            conn.execute(text("SELECT 1"))
            health_status["database"] = "connected"
            
            # Check if checkpoint tables exist (in a separate connection)
            with engine.connect() as conn2:
                result = conn2.execute(text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name IN ('checkpoints', 'checkpoint_blobs', 'checkpoint_writes')
                    ORDER BY table_name
                """))
                tables = [row[0] for row in result]
                health_status["checkpoint_tables"] = tables if tables else "missing"
            
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
