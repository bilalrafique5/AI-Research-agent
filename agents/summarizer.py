from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

def summarize(content: str, sources: list = None):
    """
    Summarize content and create structured output with confidence scores and sources.
    
    Args:
        content: The content to summarize
        sources: List of source objects with metadata
    """
    sources = sources or []
    
    prompt = f"""Extract main topics and create a structured summary.

For each topic found, provide in this EXACT format:
Topic Name: Description (confidence: XX%)

Rules:
- 5-8 key topics only
- Each topic: 1-2 sentences maximum
- Confidence score: 70-95% based on information clarity
- No bullet points
- Each topic on one new line

Content:
{content}

Format example:
Ceasefire Agreement: US and Iran agreed to a 2-week halt (confidence: 92%)
Oil Market Impact: Prices dropped below $100/barrel (confidence: 88%)"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    
    summary_text = response.choices[0].message.content
    
    # Add source information to the summary
    if sources:
        summary_text += "\n\n=== SOURCES ===" 
        for source in sources:
            if source.get("url") and source["url"] != "internal://knowledge-base":
                summary_text += f"\n• {source['source']}: {source['title']}"
                summary_text += f" (Confidence: {int(source['confidence']*100)}%)"
    
    return summary_text