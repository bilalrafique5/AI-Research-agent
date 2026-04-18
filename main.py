from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router
from api.auth import router as auth_router
from api.chat import router as chat_router

app = FastAPI(
    title="AI Research Agent",
    description="AI-powered research agent with authentication, critic evaluation, and RAG-based Q&A",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(router)
app.include_router(chat_router)

@app.get("/")
async def root():
    return {
        "message": "AI Research Agent API with RAG-based Q&A",
        "version": "1.0.0",
        "endpoints": {
            "auth": {
                "register": "POST /auth/register",
                "login": "POST /auth/login"
            },
            "research": {
                "research": "POST /api/research",
                "history": "GET /api/research-history",
                "download": "GET /api/download-report/{filename}"
            },
            "chat_qa": {
                "ask_question": "POST /api/chat/ask",
                "chat_history": "GET /api/chat/history?pdf_filename=<filename>",
                "all_sessions": "GET /api/chat/sessions",
                "delete_session": "DELETE /api/chat/session?pdf_filename=<filename>"
            }
        }
    }

