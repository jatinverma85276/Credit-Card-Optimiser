import os
import json
from pathlib import Path
from typing import Optional
from datetime import datetime
from app.graph.workflow import build_workflow
from app.models.state import AgentState

# Configuration
SESSION_DIR = Path(".sessions")
SESSION_DIR.mkdir(exist_ok=True)

def save_session(state: AgentState) -> None:
    """Save session state to a file"""
    session_file = SESSION_DIR / f"{state.session_id}.json"
    with open(session_file, 'w') as f:
        # Convert to dict and handle any non-serializable fields
        state_dict = state.dict()
        # Convert datetime objects to ISO format
        for msg in state_dict.get('conversation_history', []):
            if 'timestamp' in msg:
                msg['timestamp'] = msg['timestamp'].isoformat()
        json.dump(state_dict, f, indent=2)

def load_session(session_id: str) -> Optional[AgentState]:
    """Load session state from file"""
    session_file = SESSION_DIR / f"{session_id}.json"
    if not session_file.exists():
        return None
    
    with open(session_file, 'r') as f:
        state_data = json.load(f)
        # Convert ISO format strings back to datetime objects
        for msg in state_data.get('conversation_history', []):
            if 'timestamp' in msg:
                msg['timestamp'] = datetime.fromisoformat(msg['timestamp'])
        return AgentState(**state_data)

def get_latest_session() -> Optional[str]:
    """Get the most recent session ID"""
    sessions = list(SESSION_DIR.glob("*.json"))
    if not sessions:
        return None
    return max(sessions, key=os.path.getmtime).stem

def print_help():
    print("\nAvailable commands:")
    print("  /new     - Start a new conversation")
    print("  /history - View conversation history")
    print("  /exit    - Exit the program")
    print("  /help    - Show this help message")
    print("  /save    - Save the current session")
    print("  /load <id> - Load a specific session")

def main():
    print("Welcome to Credit Card Optimizer!")
    print("Type '/help' to see available commands\n")
    
    # Initialize workflow and state
    workflow = build_workflow()
    
    # Check for existing sessions
    latest_session = get_latest_session()
    if latest_session:
        load = input(f"Found previous session ({latest_session}). Load it? [Y/n] ").strip().lower()
        if not load or load == 'y':
            state = load_session(latest_session)
            if state:
                print(f"\nLoaded session: {state.session_id}")
                print(f"Previous conversation context loaded ({len(state.conversation_history)} messages)")
    
    # Create new session if none loaded
    if 'state' not in locals():
        state = AgentState()
        print("\nStarting a new session")
    
    print(f"\nSession ID: {state.session_id}")
    print_help()
    
    try:
        while True:
            try:
                # Get user input
                user_input = input("\nYou: ").strip()
                
                # Handle commands
                if user_input.startswith('/'):
                    cmd = user_input[1:].lower().split()[0]
                    
                    if cmd == 'exit':
                        save = input("Save this session before exiting? [Y/n] ").strip().lower()
                        if not save or save == 'y':
                            save_session(state)
                            print(f"Session saved. ID: {state.session_id}")
                        break
                        
                    elif cmd == 'new':
                        state = AgentState()
                        print(f"\nNew session started. ID: {state.session_id}")
                        continue
                        
                    elif cmd == 'history':
                        print("\n--- CONVERSATION HISTORY ---")
                        for msg in state.conversation_history:
                            print(f"{msg.role.upper()}: {msg.content}")
                        continue
                        
                    elif cmd == 'save':
                        save_session(state)
                        print(f"Session saved. ID: {state.session_id}")
                        continue
                        
                    elif cmd == 'load':
                        session_id = user_input[6:].strip()
                        if not session_id:
                            print("Please specify a session ID")
                            continue
                        loaded_state = load_session(session_id)
                        if loaded_state:
                            state = loaded_state
                            print(f"Loaded session: {state.session_id}")
                        else:
                            print(f"Session {session_id} not found")
                        continue
                        
                    elif cmd == 'help':
                        print_help()
                        continue
                
                # Add user message to history
                state.add_user_message(user_input)
                
                # Process the message
                state.raw_message = user_input
                result = workflow.invoke(state)
                
                # Extract and display the response
                if 'recommendation' in result and result['recommendation']:
                    response = result['recommendation'].get('reason', 'No specific recommendation available')
                    print(f"\nAssistant: {response}")
                    state.add_assistant_message(response)
                
                # Auto-save after each interaction
                save_session(state)
                
            except KeyboardInterrupt:
                print("\nUse '/exit' to quit or '/help' for commands")
            except Exception as e:
                error_msg = f"Error: {str(e)}"
                print(f"\n{error_msg}")
                state.add_assistant_message(error_msg)
                
    except EOFError:
        print("\nGoodbye!")
    
    print("\nThank you for using Credit Card Optimizer!")

if __name__ == "__main__":
    main()