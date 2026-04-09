from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router
from api.auth import router as auth_router

app = FastAPI(
    title="AI Research Agent",
    description="AI-powered research agent with authentication and critic evaluation",
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

@app.get("/")
async def root():
    return {
        "message": "AI Research Agent API",
        "version": "1.0.0",
        "endpoints": {
            "auth": {
                "register": "POST /auth/register",
                "login": "POST /auth/login",
                "me": "GET /auth/me"
            },
            "research": {
                "research": "POST /api/research",
                "history": "GET /api/research-history",
                "download": "GET /api/download-report/{filename}"
            }
        }
    }

