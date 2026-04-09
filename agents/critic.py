# agents/critic.py
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

def evaluate_report(report: str, original_query: str) -> dict:
    """
    Critic agent evaluates the report for:
    1. Clarity - Is the report easy to understand?
    2. Accuracy - Is the information accurate and factual?
    3. Completeness - Does it fully address the query?
    
    Returns a dict with:
    - score (0-100): overall quality score
    - passed (bool): whether report meets quality threshold (>70)
    - feedback: detailed feedback
    - issues: list of issues found
    """
    
    prompt = f"""You are a critical reviewer evaluating a research report.

Evaluate this report based on THREE criteria:
1. CLARITY: Is the language clear, well-structured, and easy to understand?
2. ACCURACY: Are the facts presented accurate and factual?
3. COMPLETENESS: Does the report fully address the query?

Report to evaluate:
---
{report}
---

Original Query: {original_query}

Provide your evaluation in this EXACT format:
CLARITY_SCORE: [0-100]
ACCURACY_SCORE: [0-100]
COMPLETENESS_SCORE: [0-100]
OVERALL_SCORE: [0-100]
PASSED: [YES/NO] (YES if overall >= 70, NO otherwise)

ISSUES_FOUND:
[List 3-5 specific issues if any, or write "None" if report is good]

FEEDBACK:
[2-3 sentences of constructive feedback]

RECOMMENDATION:
[If PASSED=NO, explain what needs to be fixed. If PASSED=YES, write "Report is ready to publish."]"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    
    evaluation_text = response.choices[0].message.content
    
    # Parse the evaluation
    result = parse_evaluation(evaluation_text)
    
    return result

def parse_evaluation(evaluation_text: str) -> dict:
    """Parse the critic's evaluation response"""
    
    lines = evaluation_text.split('\n')
    result = {
        "clarity_score": 0,
        "accuracy_score": 0,
        "completeness_score": 0,
        "overall_score": 0,
        "passed": False,
        "issues": [],
        "feedback": "",
        "recommendation": ""
    }
    
    current_section = None
    issues_text = []
    feedback_text = []
    recommendation_text = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        if line.startswith("CLARITY_SCORE:"):
            try:
                result["clarity_score"] = int(line.split(":")[-1].strip())
            except:
                pass
        elif line.startswith("ACCURACY_SCORE:"):
            try:
                result["accuracy_score"] = int(line.split(":")[-1].strip())
            except:
                pass
        elif line.startswith("COMPLETENESS_SCORE:"):
            try:
                result["completeness_score"] = int(line.split(":")[-1].strip())
            except:
                pass
        elif line.startswith("OVERALL_SCORE:"):
            try:
                result["overall_score"] = int(line.split(":")[-1].strip())
            except:
                pass
        elif line.startswith("PASSED:"):
            result["passed"] = "YES" in line.upper()
        elif line.startswith("ISSUES_FOUND:"):
            current_section = "issues"
        elif line.startswith("FEEDBACK:"):
            current_section = "feedback"
        elif line.startswith("RECOMMENDATION:"):
            current_section = "recommendation"
        elif current_section == "issues":
            if line and not line.startswith("-") and not line.startswith("•"):
                if line.lower() != "none":
                    issues_text.append(line)
        elif current_section == "feedback":
            if line:
                feedback_text.append(line)
        elif current_section == "recommendation":
            if line:
                recommendation_text.append(line)
    
    result["issues"] = issues_text
    result["feedback"] = " ".join(feedback_text)
    result["recommendation"] = " ".join(recommendation_text)
    
    # If overall_score is 0, calculate from component scores
    if result["overall_score"] == 0:
        result["overall_score"] = (
            result["clarity_score"] + 
            result["accuracy_score"] + 
            result["completeness_score"]
        ) // 3
    
    return result

def should_regenerate(evaluation: dict) -> bool:
    """Determine if report should be regenerated"""
    return not evaluation["passed"]
