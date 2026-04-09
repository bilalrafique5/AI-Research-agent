from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

def generate_report(summary: str):
    prompt = f"""Create a structured research report with confidence indicators.

Format the report with:
1. EXECUTIVE SUMMARY (2-3 sentences, confidence: X%)
2. KEY FINDINGS (structured as "Topic: Description (confidence: X%)")
3. SOURCES
4. CONCLUSION (1-2 sentences)

The summary already contains topics with confidence scores - preserve those.
Extract the SOURCES section from the summary if present.

Summary content:
{summary}

Guidelines:
- Maintain confidence scores from the summary
- List all sources with their confidence levels
- Use clear, professional language
- Be concise and well-organized"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return response.choices[0].message.content