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
    Execute research workflow and generate PDF report
    """
    query = request.query
    
    # Run the complete workflow
    result = await run_workflow(query)

    return {
        "status": "success",
        "result": {
            "plan": result["plan"],
            "summary": result["summary"],
            "report": result["report"],
            "pdf_path": result["pdf_path"],
            "message": "PDF report generated successfully"
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