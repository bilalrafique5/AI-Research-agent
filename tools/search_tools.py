from tavily import TavilyClient
import os
from dotenv import load_dotenv

load_dotenv()

tavily_api_key = os.getenv("TAVILY_API_KEY")
client = TavilyClient(api_key=tavily_api_key) if tavily_api_key else None

def search_web(query: str):
    """
    Search the web using Tavily API with error handling.
    Returns search results with sources preserved.
    """
    if not client:
        return get_fallback_results(query, "Tavily API not configured")
    
    try:
        response = client.search(query=query, max_results=5)
        results = response.get("results", [])
        
        # Preserve source information
        enriched_results = []
        for result in results:
            enriched_results.append({
                "title": result.get("title", ""),
                "content": result.get("content", ""),
                "url": result.get("url", ""),
                "source": extract_domain(result.get("url", "")),
                "confidence": 0.95  # High confidence for live search
            })
        return enriched_results
    except Exception as e:
        print(f"Search failed: {str(e)}")
        return get_fallback_results(query, str(e))

def get_fallback_results(query: str, error_reason: str) -> list:
    """
    Provide fallback results when search fails.
    Returns mock data with sources so the workflow can continue.
    """
    return [
        {
            "title": f"Knowledge Base: {query}",
            "content": f"Unable to fetch live search results ({error_reason}). Using knowledge-based response for: {query}",
            "url": "internal://knowledge-base",
            "source": "Internal Knowledge Base",
            "confidence": 0.70  # Lower confidence for fallback
        }
    ]

def extract_domain(url: str) -> str:
    """Extract domain from URL"""
    if not url:
        return "Unknown Source"
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        domain = parsed.netloc.replace("www.", "")
        return domain if domain else "Unknown Source"
    except:
        return "Unknown Source"