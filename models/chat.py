# models/chat.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class ChatMessage(BaseModel):
    """Individual chat message"""
    role: str = Field(..., description="'user' or 'assistant'")
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ChatRequest(BaseModel):
    """Chat question request"""
    question: str = Field(..., min_length=1, max_length=1000)
    pdf_filename: str

class ChatResponse(BaseModel):
    """Chat response with sources"""
    answer: str
    sources: List[dict] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ChatSession(BaseModel):
    """Chat conversation session"""
    username: str
    pdf_filename: str
    pdf_path: str
    conversation: List[ChatMessage] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    message_count: int = 0
