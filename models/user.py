# models/user.py
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime

class UserRegister(BaseModel):
    """User registration model"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "john_doe",
                "email": "john@example.com",
                "password": "securepassword123",
                "full_name": "John Doe"
            }
        }

class UserLogin(BaseModel):
    """User login model"""
    username: str = Field(..., min_length=3)
    password: str = Field(..., min_length=6)
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "john_doe",
                "password": "securepassword123"
            }
        }

class UserResponse(BaseModel):
    """User response model (without password)"""
    username: str
    email: str
    full_name: Optional[str] = None
    created_at: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "john_doe",
                "email": "john@example.com",
                "full_name": "John Doe",
                "created_at": "2024-01-01T12:00:00"
            }
        }

class Token(BaseModel):
    """Token response model"""
    access_token: str
    token_type: str = "bearer"
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }

class TokenData(BaseModel):
    """Token data model"""
    username: Optional[str] = None
    exp: Optional[float] = None
