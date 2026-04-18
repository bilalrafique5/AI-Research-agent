# agents/qa_agent.py
"""
Q&A Agent using Groq API
Answers questions based on retrieved document context
"""
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

def answer_question(question: str, context: str, chat_history: list = None) -> dict:
    """
    Answer a question using the given document context
    
    Args:
        question: User's question
        context: Retrieved context from PDF chunks
        chat_history: Previous conversation messages
    
    Returns:
        Dictionary with answer, confidence, and metadata
    """
    
    # System prompt
    system_prompt = """You are a helpful AI assistant answering questions about a research document.
Use the provided document excerpts to answer the question accurately.
If the information is not in the provided context, say "This information is not available in the provided document."
Be concise and specific in your answers."""
    
    # Build conversation history for context
    messages = [
        {"role": "system", "content": system_prompt}
    ]
    
    if chat_history:
        for msg in chat_history:
            # Handle both dict and potential nested structures
            if isinstance(msg, dict):
                # Filter to only include role and content
                role = msg.get("role", "user")
                content = msg.get("content", "")
                if role and content:  # Only add if both present
                    messages.append({
                        "role": role,
                        "content": content
                    })
            # Keep last 4 messages for context
            if len(messages) > 5:  # 1 system + 4 history messages max
                messages = messages[:5]
    
    # Add current question with context
    user_message = f"""Document Context:
{context}

Question: {question}

Please answer based on the document context provided above."""
    
    messages.append({
        "role": "user",
        "content": user_message
    })
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.3,
            max_tokens=800
        )
        
        answer = response.choices[0].message.content
        
        # Determine confidence based on context quality
        confidence = 0.85 if context and len(context) > 100 else 0.5
        
        return {
            "answer": answer,
            "confidence": confidence,
            "tokens_used": {
                "prompt": response.usage.prompt_tokens,
                "completion": response.usage.completion_tokens
            }
        }
    
    except Exception as e:
        return {
            "answer": f"Error processing question: {str(e)}",
            "confidence": 0.0,
            "error": str(e)
        }


def summarize_conversation(messages: list) -> str:
    """
    Summarize a conversation for context
    
    Args:
        messages: List of chat messages
    
    Returns:
        Conversation summary
    """
    if not messages or len(messages) < 2:
        return ""
    
    conversation = "\n".join([f"{msg['role']}: {msg['content'][:100]}" for msg in messages[-5:]])
    
    prompt = f"""Summarize this conversation in 1-2 sentences:
{conversation}"""
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=100
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        return ""
