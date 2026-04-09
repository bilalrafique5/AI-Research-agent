from fastapi import APIRouter
from starlette.responses import FileResponse
from pydantic import BaseModel
from services.workflow import run_workflow
import os

router = APIRouter()

class ResearchRequest(BaseModel):
    query: str

@router.post("/research")
async def research(request: ResearchRequest):
    """
    Execute research workflow with critic evaluation and generate PDF report
    Flow: Planner → Research → Summarizer (with sources & confidence) → Report → Critic → PDF
    """
    query = request.query
    
    # Run the complete workflow
    result = await run_workflow(query)

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

@router.get("/download-report/{filename}")
async def download_report(filename: str):
    """
    Download the generated PDF report
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