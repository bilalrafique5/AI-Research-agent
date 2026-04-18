# api/chat.py
"""
Chat endpoints for Q&A over research PDFs
"""
from fastapi import APIRouter, HTTPException, status, Depends, Query
from api.dependencies import get_current_user
from config.database import db
from models.chat import ChatRequest, ChatResponse, ChatMessage
from agents.qa_agent import answer_question, summarize_conversation
from tools.rag_engine import RAGEngine
from datetime import datetime
from bson import ObjectId
import os

router = APIRouter(prefix="/api/chat", tags=["Chat"])

# Global RAG engine instance
rag_engines = {}  # Dictionary to store RAG engines per PDF

def get_rag_engine(pdf_path: str) -> RAGEngine:
    """Get or create RAG engine for PDF"""
    if pdf_path not in rag_engines:
        engine = RAGEngine(chunk_size=600, chunk_overlap=150)
        try:
            engine.build_index(pdf_path)
            rag_engines[pdf_path] = engine
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to load PDF: {str(e)}"
            )
    return rag_engines[pdf_path]


@router.post("/ask", response_model=ChatResponse)
async def ask_question(
    request: ChatRequest,
    user: dict = Depends(get_current_user)
):
    """
    Ask a question about a specific PDF research report
    
    Args:
        request: Chat request with question and pdf_filename
        user: Current authenticated user
    
    Returns:
        Answer with sources and confidence score
    """
    
    # Verify user owns this research
    research = db.research_history.find_one({
        "username": user["username"],
        "result.pdf_filename": request.pdf_filename
    })
    
    if not research:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Research PDF not found"
        )
    
    # Get PDF path
    reports_dir = os.path.join(os.path.dirname(__file__), "..", "reports")
    pdf_path = os.path.join(reports_dir, request.pdf_filename)
    
    if not os.path.exists(pdf_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PDF file not found on server"
        )
    
    # Get or create RAG engine
    rag_engine = get_rag_engine(pdf_path)
    
    # Retrieve relevant context
    context = rag_engine.build_context(request.question, top_k=5)
    
    if not context:
        context = "No relevant context found in the document."
    
    # Get chat session
    chat_session = db.chat_sessions.find_one({
        "username": user["username"],
        "pdf_filename": request.pdf_filename
    })
    
    chat_history = []
    if chat_session:
        chat_history = chat_session.get("conversation", [])
    
    # Get answer from Groq using RAG context
    qa_result = answer_question(
        question=request.question,
        context=context,
        chat_history=chat_history
    )
    
    # Extract sources from context
    sources = []
    if context and "Source" in context:
        # Parse sources from context
        lines = context.split("\n")
        for line in lines:
            if "[Source" in line:
                sources.append({"text": line})
    
    # Create response
    response = ChatResponse(
        answer=qa_result["answer"],
        sources=sources,
        confidence=qa_result.get("confidence", 0.7)
    )
    
    # Store conversation in MongoDB
    user_message = ChatMessage(role="user", content=request.question)
    assistant_message = ChatMessage(role="assistant", content=response.answer)
    
    if chat_session:
        # Update existing session with $each to avoid nested arrays
        db.chat_sessions.update_one(
            {"_id": chat_session["_id"]},
            {
                "$push": {
                    "conversation": {
                        "$each": [
                            user_message.dict(),
                            assistant_message.dict()
                        ]
                    }
                },
                "$set": {"updated_at": datetime.utcnow()},
                "$inc": {"message_count": 2}
            }
        )
    else:
        # Create new session
        new_session = {
            "username": user["username"],
            "pdf_filename": request.pdf_filename,
            "pdf_path": pdf_path,
            "conversation": [
                user_message.dict(),
                assistant_message.dict()
            ],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "message_count": 2
        }
        db.chat_sessions.insert_one(new_session)
    
    return response


@router.get("/history")
async def get_chat_history(
    pdf_filename: str = Query(..., description="PDF filename to get chat history for"),
    user: dict = Depends(get_current_user)
):
    """
    Get chat history for a specific PDF
    
    Args:
        pdf_filename: Name of the PDF file
        user: Current authenticated user
    
    Returns:
        Chat conversation history
    """
    
    chat_session = db.chat_sessions.find_one({
        "username": user["username"],
        "pdf_filename": pdf_filename
    })
    
    if not chat_session:
        return {
            "pdf_filename": pdf_filename,
            "conversation": [],
            "message_count": 0,
            "created_at": None
        }
    
    return {
        "pdf_filename": pdf_filename,
        "conversation": chat_session.get("conversation", []),
        "message_count": chat_session.get("message_count", 0),
        "created_at": chat_session.get("created_at"),
        "updated_at": chat_session.get("updated_at")
    }


@router.delete("/session")
async def delete_chat_session(
    pdf_filename: str = Query(..., description="PDF filename"),
    user: dict = Depends(get_current_user)
):
    """
    Delete chat session for a PDF
    
    Args:
        pdf_filename: Name of the PDF file
        user: Current authenticated user
    
    Returns:
        Success message
    """
    
    result = db.chat_sessions.delete_one({
        "username": user["username"],
        "pdf_filename": pdf_filename
    })
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    # Clear RAG engine cache for this PDF
    reports_dir = os.path.join(os.path.dirname(__file__), "..", "reports")
    pdf_path = os.path.join(reports_dir, pdf_filename)
    
    if pdf_path in rag_engines:
        del rag_engines[pdf_path]
    
    return {"message": "Chat session deleted successfully"}


@router.get("/sessions")
async def get_all_chat_sessions(user: dict = Depends(get_current_user)):
    """
    Get all chat sessions for current user
    
    Returns:
        List of chat sessions with metadata
    """
    
    sessions = list(db.chat_sessions.find(
        {"username": user["username"]},
        {"conversation": 0}  # Exclude full conversation
    ))
    
    # Convert ObjectId to string
    for session in sessions:
        session["_id"] = str(session["_id"])
    
    return {
        "sessions": sessions,
        "total": len(sessions)
    }
