from tavily import TavilyClient
import os
from dotenv import load_dotenv
from config.secret_manager import get_flag  # ← Add karo

load_dotenv()

tavily_api_key = os.getenv("TAVILY_API_KEY")
client = TavilyClient(api_key=tavily_api_key) if tavily_api_key else None

def search_web(query: str):
    """
    Search the web using Tavily API with error handling.
    """
    # ← Flag check karo
    if not get_flag("TAVILY_SEARCH_ENABLED"):
        print("🔴 Tavily Search is DISABLED by admin")
        return get_fallback_results(query, "Tavily search disabled by admin")
    
    if not client:
        return get_fallback_results(query, "Tavily API not configured")
    
    try:
        response = client.search(query=query, max_results=5)
        results = response.get("results", [])
        enriched_results = []
        for result in results:
            enriched_results.append({
                "title": result.get("title", ""),
                "content": result.get("content", ""),
                "url": result.get("url", ""),
                "source": extract_domain(result.get("url", "")),
                "confidence": 0.95
            })
        return enriched_results
    except Exception as e:
        print(f"Search failed: {str(e)}")
        return get_fallback_results(query, str(e))

def get_fallback_results(query: str, error_reason: str) -> list:
    return [
        {
            "title": f"Knowledge Base: {query}",
            "content": f"Unable to fetch live search results ({error_reason}). Using knowledge-based response for: {query}",
            "url": "internal://knowledge-base",
            "source": "Internal Knowledge Base",
            "confidence": 0.70
        }
    ]

def extract_domain(url: str) -> str:
    if not url:
        return "Unknown Source"
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        domain = parsed.netloc.replace("www.", "")
        return domain if domain else "Unknown Source"
    except:
        return "Unknown Source"