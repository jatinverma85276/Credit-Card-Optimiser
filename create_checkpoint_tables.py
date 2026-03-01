#!/usr/bin/env python3
"""
Manual script to create LangGraph checkpoint tables
Run this in Render Shell if build.sh didn't create them
"""
import os
from langgraph.checkpoint.postgres import PostgresSaver

def create_checkpoint_tables():
    """Create checkpoint tables manually"""
    # Get DATABASE_URL from environment
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("❌ ERROR: DATABASE_URL not found in environment variables")
        return
    
    print(f"🔗 Connecting to database...")
    print(f"   Host: {database_url.split('@')[1].split('/')[0] if '@' in database_url else 'unknown'}")
    
    try:
        print("🔧 Creating LangGraph checkpoint tables...")
        
        # Initialize PostgresSaver - this creates the tables
        with PostgresSaver.from_conn_string(database_url) as checkpointer:
            print("✅ Checkpoint tables created successfully!")
            print("   Tables created:")
            print("   - checkpoints")
            print("   - checkpoint_blobs")
            print("   - checkpoint_writes")
            
    except Exception as e:
        print(f"❌ Error creating checkpoint tables: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    create_checkpoint_tables()
    print("\n🎉 Done! You can now use the /chat endpoint.")
