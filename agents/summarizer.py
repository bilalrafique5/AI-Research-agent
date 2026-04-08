from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

def summarize(content: str):
    prompt = f"""Summarize the content concisely and clearly.

Provide ONLY:
- 5-8 key bullet points
- Each point: 1 sentence maximum
- Focus on main ideas and important details
- Use clear, simple language
- NO extra explanation needed

Content: {content}

Output as bullet points only:
• [key point]
• [key point]
Etc."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return response.choices[0].message.content