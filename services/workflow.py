# services/workflow.py
from agents.planner import plan_task
from agents.search import search_agent
from agents.summarizer import summarize
from agents.report import generate_report
from agents.critic import evaluate_report, should_regenerate
from tools.pdf_generator import generate_research_pdf
from config.secret_manager import get_flag  # ← Add karo
from fastapi import HTTPException          # ← Add karo

async def run_workflow(query: str):
    
    # ← Sabse pehle flag check karo
    if not get_flag("TAVILY_SEARCH_ENABLED"):
        raise HTTPException(
            status_code=503,
            detail={
                "status": "disabled",
                "message": "Research service is currently disabled by admin. Please try again later."
            }
        )
    
    # Step 1: Planning
    plan = plan_task(query)

    # Step 2: Search
    search_status = "success"
    try:
        results = search_agent(query)
    except Exception as e:
        print(f"Search failed: {str(e)}. Continuing with knowledge-based approach.")
        search_status = f"failed: {str(e)}"
        results = [{"content": f"Knowledge-based response for: {query}"}]

    combined = ""
    sources = []
    for r in results:
        combined += r.get("content", "") + "\n"
        source_info = {
            "title": r.get("title", ""),
            "url": r.get("url", ""),
            "source": r.get("source", "Unknown"),
            "confidence": r.get("confidence", 0.7)
        }
        sources.append(source_info)

    # Step 3: Summarize
    summary = summarize(combined, sources)

    # Step 4: Report Generation
    report = generate_report(summary)
    
    # Step 5: Critic Evaluation
    evaluation = evaluate_report(report, query)
    regeneration_count = 0
    max_regenerations = 2
    
    # Step 6: Auto-regenerate if needed
    while should_regenerate(evaluation) and regeneration_count < max_regenerations:
        regeneration_count += 1
        feedback_prompt = f"Previous report issues:\n{chr(10).join(evaluation['issues'])}\n\nFeedback: {evaluation['recommendation']}"
        report = generate_report(summary + "\n\n" + feedback_prompt)
        evaluation = evaluate_report(report, query)
    
    # Step 7: Generate PDF
    pdf_result = generate_research_pdf(report, query)

    return {
        "plan": plan,
        "summary": summary,
        "sources": sources,
        "report": report,
        "evaluation": evaluation,
        "regeneration_count": regeneration_count,
        "search_status": search_status,
        "pdf_path": pdf_result["path"],
        "pdf_filename": pdf_result["filename"]
    }