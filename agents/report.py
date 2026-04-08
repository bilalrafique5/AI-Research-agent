from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

def generate_report(summary: str):
    prompt = f"""Create a structured research report from this summary.

Include these sections:
1. EXECUTIVE SUMMARY (3-4 sentences)
2. KEY FINDINGS (5-7 bullet points, concise)
3. RECOMMENDATIONS (3-5 actionable items)
4. CONCLUSION (2-3 sentences)

Be concise, professional, and easy to read.

Summary: {summary}"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]  ,
        temperature=0
    )

    return response.choices[0].message.content