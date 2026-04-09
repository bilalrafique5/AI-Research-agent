# api/auth.py
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from config.database import db
from models.user import UserRegister, Token, UserLogin
from utils.auth import hash_password, verify_password, create_access_token, verify_token
from datetime import datetime
from jose import JWTError

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister):
    """
    Register a new user
    
    - **username**: unique username (3-50 characters)
    - **email**: valid email address
    - **password**: password (minimum 6 characters)
    - **full_name**: optional full name
    """
    
    # Check if user already exists
    existing_user = db.users.find_one({
        "$or": [
            {"username": user_data.username.lower()},
            {"email": user_data.email.lower()}
        ]
    })
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )
    
    # Create new user
    hashed_password = hash_password(user_data.password)
    
    user_doc = {
        "username": user_data.username.lower(),
        "email": user_data.email.lower(),
        "full_name": user_data.full_name or "",
        "hashed_password": hashed_password,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = db.users.insert_one(user_doc)
    
    # Create access token
    access_token = create_access_token(data={"sub": user_data.username.lower()})
    
    return Token(
        access_token=access_token,
        token_type="bearer"
    )

@router.post("/login", response_model=Token)
async def login(user_data: UserLogin):
    """
    User login with username and password.
    Returns access token (JWT) for use in protected endpoints.
    """
    # Find user by username
    user = db.users.find_one({"username": user_data.username.lower()})
    
    if not user or not verify_password(user_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": user_data.username.lower()})
    
    return Token(
        access_token=access_token,
        token_type="bearer"
    )


