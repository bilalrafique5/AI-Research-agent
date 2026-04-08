from fastapi import APIRouter
from pydantic import BaseModel
from agents import planner, summarizer, report

router = APIRouter()

class ResearchRequest(BaseModel):
    query: str

@router.post("/research")
async def research(request: ResearchRequest):
    query = request.query

    # Generate structured plan
    plan_text = planner.plan_task(query)
    plan_lines = [line.strip() for line in plan_text.splitlines() if line.strip()]

    # Generate structured summary
    summary_text = summarizer.summarize("\n".join(plan_lines))
    summary_lines = [line.strip() for line in summary_text.splitlines() if line.strip()]

    # Generate structured report
    report_text = report.generate_report("\n".join(summary_lines))
    report_lines = [line.strip() for line in report_text.splitlines() if line.strip()]

    return {
        "result": {
            "plan": plan_lines,
            "summary": summary_lines,
            "report": report_lines
        }
    }