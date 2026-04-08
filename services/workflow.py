from agents.planner import plan_task
from agents.search import search_agent
from agents.summarizer import summarize
from agents.report import generate_report

async def run_workflow(query: str):
    # Step 1: Planning
    plan = plan_task(query)

    # Step 2: Search
    results = search_agent(query)

    combined = ""
    for r in results:
        combined += r.get("content", "") + "\n"

    # Step 3: Summarize
    summary = summarize(combined)

    # Step 4: Report
    report = generate_report(summary)

    return {
        "plan": plan,
        "summary": summary,
        "report": report
    }