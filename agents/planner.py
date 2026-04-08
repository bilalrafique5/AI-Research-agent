# agents/planner.py
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)
def plan_task(query: str):
    prompt = f"""Break down the research task into clear, actionable steps.

Provide ONLY:
1. A numbered list (max 5-7 steps)
2. Each step should be concise (1 sentence maximum)
3. Start each step with an action verb
4. Make it specific and measurable

Task: {query}

Output Format:
1. [Action verb] - [specific task]
2. [Action verb] - [specific task]
Etc."""

    response = client.chat.completions.create(
         model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return response.choices[0].message.content