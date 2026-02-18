from app.db.database import SessionLocal
from app.db.models import UserMemory

def migrate_memories():
    """Migrate all existing memories to use 'default_user' as user_id"""
    db = SessionLocal()
    try:
        # Get all memories
        memories = db.query(UserMemory).all()
        print(f"Found {len(memories)} memories")
        
        # Update all to use default_user
        for mem in memories:
            old_user_id = mem.user_id
            mem.user_id = "default_user"
            print(f"  Migrated: {mem.memory_text} (from {old_user_id[:20]}...)")
        
        db.commit()
        print(f"\n✅ Successfully migrated {len(memories)} memories to 'default_user'")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    migrate_memories()
