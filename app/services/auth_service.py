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
    Hash a password using bcrypt with SHA256 pre-hashing
    
    Why SHA256 first?
    - Bcrypt has a 72-byte limit
    - SHA256 always produces 64-character hex string (well under 72 bytes)
    - This allows passwords of ANY length
    - Industry standard approach (used by Django, etc.)
    """
    # Pre-hash with SHA256 to handle any password length
    password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
    print(password_hash, "Password hased   ")
    
    # Then hash with bcrypt for security
    return pwd_context.hash(password_hash)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash
    Must apply same SHA256 pre-hashing
    """
    # Pre-hash with SHA256 (same as during hashing)
    password_hash = hashlib.sha256(plain_password.encode('utf-8')).hexdigest()
    
    # Verify with bcrypt
    return pwd_context.verify(password_hash, hashed_password)

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
    print(password,"Password")
    # Create user with hashed password
    hashed_password = hash_password(password)
    print(hashed_password,"Hashed Password")

    
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
