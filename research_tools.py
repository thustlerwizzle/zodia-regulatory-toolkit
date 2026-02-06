"""
Research Tools for fetching regulatory information from various sources
"""
import json
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import requests
from newsapi import NewsApiClient
from config import (
    NEWSAPI_KEY,
    MAX_NEWS_ARTICLES
)


class ResearchTools:
    """Collection of research tools for regulatory analysis"""
    
    def __init__(self):
        self.newsapi_client = NewsApiClient(api_key=NEWSAPI_KEY) if NEWSAPI_KEY else None
    
    def search_news(self, query: str, jurisdiction: str = None, days: int = 30) -> List[Dict]:
        """Search news articles using NewsAPI"""
        if not self.newsapi_client:
            return []
        
        try:
            # Build query with jurisdiction if provided
            search_query = query
            if jurisdiction:
                search_query = f"{query} {jurisdiction}"
            
            # Calculate date range
            to_date = datetime.now()
            from_date = to_date - timedelta(days=days)
            
            response = self.newsapi_client.get_everything(
                q=search_query,
                language="en",
                sort_by="relevancy",
                from_param=from_date.strftime("%Y-%m-%d"),
                to=to_date.strftime("%Y-%m-%d"),
                page_size=min(MAX_NEWS_ARTICLES, 100)
            )
            
            results = []
            for article in response.get("articles", []):
                results.append({
                    "title": article.get("title", ""),
                    "url": article.get("url", ""),
                    "content": article.get("description", ""),
                    "author": article.get("author", ""),
                    "published_at": article.get("publishedAt", ""),
                    "source": article.get("source", {}).get("name", "NewsAPI"),
                    "timestamp": datetime.now().isoformat()
                })
            return results
        except Exception as e:
            error_msg = str(e)
            if "403" in error_msg or "Forbidden" in error_msg:
                print(f"NewsAPI search error: Forbidden (403) - Check your NEWSAPI_KEY")
            elif "401" in error_msg or "Unauthorized" in error_msg:
                print(f"NewsAPI search error: Unauthorized (401) - Invalid API key")
            elif "429" in error_msg or "rate limit" in error_msg.lower():
                print(f"NewsAPI search error: Rate limit exceeded")
            else:
                print(f"NewsAPI search error: {e}")
            return []
    
    def search_regulatory_updates(
        self, 
        topic: str, 
        jurisdiction: str = None,
        use_news: bool = True
    ) -> Dict[str, List[Dict]]:
        """Comprehensive regulatory search using NewsAPI"""
        # Build search query - be smarter about avoiding redundancy
        topic_lower = topic.lower()
        
        # If topic already contains regulatory terms, use it as-is or simplify
        if any(term in topic_lower for term in ["regulation", "regulatory", "compliance", "policy"]):
            # Use topic as primary query, maybe add jurisdiction
            base_query = topic
        else:
            # Add regulatory terms if not present
            base_query = f"{topic} regulation"
        
        # Add jurisdiction if provided
        if jurisdiction:
            query = f"{base_query} {jurisdiction}"
        else:
            query = base_query
        
        all_results = {
            "news": [],
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "errors": []
        }
        
        # Try news search with primary query (limit to 7 days for faster results)
        if use_news:
            try:
                all_results["news"] = self.search_news(query, jurisdiction, days=7)
                
                # If no results with full query, try simpler version
                if len(all_results["news"]) == 0 and len(query) > 50:
                    # Try with just the core topic terms
                    simple_query = " ".join(topic.split()[:5])  # First 5 words
                    if jurisdiction:
                        simple_query = f"{simple_query} {jurisdiction}"
                    all_results["news"] = self.search_news(simple_query, jurisdiction, days=7)
                    if len(all_results["news"]) > 0:
                        all_results["query"] = simple_query  # Update query to what worked
                        
            except Exception as e:
                all_results["errors"].append(f"NewsAPI error: {str(e)}")
        
        # Log if no results
        total_results = len(all_results["news"])
        if total_results == 0 and all_results["errors"]:
            print(f"Warning: No research results found. Errors: {', '.join(all_results['errors'])}")
        
        return all_results
    
    def get_all_sources(self, results: Dict[str, List[Dict]]) -> List[Dict]:
        """Extract and deduplicate all sources from research results"""
        sources = []
        seen_urls = set()
        
        for source_type in ["news"]:
            for result in results.get(source_type, []):
                url = result.get("url", "")
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    sources.append({
                        "title": result.get("title", ""),
                        "url": url,
                        "source_type": source_type,
                        "timestamp": result.get("timestamp", "")
                    })
        
        return sources

