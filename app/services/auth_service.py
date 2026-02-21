"""
Authentication service for user signup and login
"""
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.db.models import UserAuth
import uuid
import hashlib

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt
    Bcrypt has a 72-byte limit, so we truncate to 72 bytes
    """
    # Truncate password to 72 bytes to avoid bcrypt limit
    password_bytes = password.encode('utf-8')[:72]
    password = password_bytes.decode('utf-8', errors='ignore')
    
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash
    Applies same truncation logic for consistency
    """
    # Truncate password to 72 bytes (same as during hashing)
    password_bytes = plain_password.encode('utf-8')[:72]
    plain_password = password_bytes.decode('utf-8', errors='ignore')
    
    return pwd_context.verify(plain_password, hashed_password)

def create_user(db: Session, email: str, name: str, password: str) -> UserAuth:
    """
    Create a new user with hashed password
    Returns the created user or raises exception if email exists
    """
    # Check if user already exists
    existing_user = db.query(UserAuth).filter(UserAuth.email == email).first()
    if existing_user:
        raise ValueError("Email already registered")
    
    # Generate unique user_id
    user_id = f"user_{uuid.uuid4().hex[:16]}"
    
    # Create user with hashed password
    hashed_password = hash_password(password)
    
    new_user = UserAuth(
        user_id=user_id,
        email=email,
        name=name,
        hashed_password=hashed_password,
        is_active=True
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

def authenticate_user(db: Session, email: str, password: str) -> UserAuth:
    """
    Authenticate user with email and password
    Returns user if authentication successful, None otherwise
    """
    user = db.query(UserAuth).filter(UserAuth.email == email).first()
    
    if not user:
        return None
    
    if not user.is_active:
        return None
    
    if not verify_password(password, user.hashed_password):
        return None
    
    return user

def get_user_by_email(db: Session, email: str) -> UserAuth:
    """Get user by email"""
    return db.query(UserAuth).filter(UserAuth.email == email).first()

def get_user_by_user_id(db: Session, user_id: str) -> UserAuth:
    """Get user by user_id"""
    return db.query(UserAuth).filter(UserAuth.user_id == user_id).first()
