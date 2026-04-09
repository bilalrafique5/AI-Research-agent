from fastapi import APIRouter, Depends, HTTPException, status
from starlette.responses import FileResponse
from pydantic import BaseModel
from services.workflow import run_workflow
from api.dependencies import get_current_user
from config.database import db
from datetime import datetime
from bson import ObjectId
import os

router = APIRouter(prefix="/api")

class ResearchRequest(BaseModel):
    query: str

@router.post("/research")
async def research(request: ResearchRequest, user: dict = Depends(get_current_user)):
    """
    Execute research workflow with critic evaluation and generate PDF report
    Flow: Planner → Research → Summarizer (with sources & confidence) → Report → Critic → PDF
    
    Requires authentication with Bearer token
    """
    query = request.query
    
    # Run the complete workflow
    result = await run_workflow(query)

    # Store research in user's history
    research_record = {
        "username": user["username"],
        "query": query,
        "created_at": datetime.utcnow(),
        "result": {
            "plan": result["plan"],
            "overall_score": result["evaluation"]["overall_score"],
            "sources_count": len(result["sources"]),
            "pdf_path": result["pdf_path"]
        }
    }
    
    db.research_history.insert_one(research_record)

    return {
        "status": "success",
        "result": {
            "plan": result["plan"],
            "summary": result["summary"],
            "sources": [
                {
                    "title": s["title"],
                    "url": s["url"],
                    "domain": s["source"],
                    "confidence": f"{int(s['confidence']*100)}%"
                } for s in result["sources"]
            ],
            "report": result["report"],
            "evaluation": {
                "clarity_score": result["evaluation"]["clarity_score"],
                "accuracy_score": result["evaluation"]["accuracy_score"],
                "completeness_score": result["evaluation"]["completeness_score"],
                "overall_score": result["evaluation"]["overall_score"],
                "passed": result["evaluation"]["passed"],
                "feedback": result["evaluation"]["feedback"],
                "issues": result["evaluation"]["issues"],
                "recommendation": result["evaluation"]["recommendation"]
            },
            "search_status": result["search_status"],
            "regeneration_count": result["regeneration_count"],
            "pdf_path": result["pdf_path"],
            "message": "Research completed with sources and confidence scores"
        }
    }

@router.get("/research-history")
async def get_research_history(user: dict = Depends(get_current_user)):
    """
    Get user's research history
    
    Requires authentication with Bearer token
    """
    history = list(db.research_history.find(
        {"username": user["username"]},
        {"_id": 1, "query": 1, "created_at": 1, "result": 1}
    ).sort("created_at", -1).limit(20))
    
    # Convert ObjectId to string for JSON serialization
    for record in history:
        record["_id"] = str(record["_id"])
    
    return {
        "status": "success",
        "count": len(history),
        "history": history
    }

@router.get("/download-report/{filename}")
async def download_report(filename: str, user: dict = Depends(get_current_user)):
    """
    Download the generated PDF report
    
    Requires authentication with Bearer token
    """
    pdf_dir = os.path.join(os.path.dirname(__file__), "..", "reports")
    file_path = os.path.join(pdf_dir, filename)
    
    # Security check - ensure file is in reports directory
    if not os.path.abspath(file_path).startswith(os.path.abspath(pdf_dir)):
        return {"error": "Invalid file path"}
    
    if not os.path.exists(file_path):
        return {"error": "File not found"}
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/pdf"
    )