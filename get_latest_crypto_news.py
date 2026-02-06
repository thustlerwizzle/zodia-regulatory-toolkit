"""
Get the latest cryptocurrency regulation news articles directly
"""
from research_tools import ResearchTools
from datetime import datetime

def main():
    print("=" * 80)
    print("📰 LATEST CRYPTOCURRENCY REGULATION NEWS")
    print("=" * 80)
    print(f"📅 Date Range: Last 7 days (as of {datetime.now().strftime('%Y-%m-%d %H:%M')})")
    print()
    
    # Initialize research tools
    tools = ResearchTools()
    
    if not tools.newsapi_client:
        print("❌ NewsAPI not configured. Please check your API key.")
        return
    
    # Search queries for crypto regulation news
    queries = [
        "cryptocurrency regulation",
        "crypto regulation",
        "digital asset regulation",
        "stablecoin regulation",
        "DeFi regulation",
        "crypto exchange regulation"
    ]
    
    all_articles = []
    seen_urls = set()
    
    print("🔍 Fetching latest news articles...")
    print()
    
    for query in queries:
        print(f"   Searching: {query}...", end=" ")
        try:
            articles = tools.search_news(query, days=7)
            count = 0
            for article in articles:
                url = article.get('url', '')
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    all_articles.append(article)
                    count += 1
            print(f"Found {count} new articles")
        except Exception as e:
            print(f"Error: {str(e)}")
    
    # Sort by published date (newest first)
    all_articles.sort(key=lambda x: x.get('published_at', ''), reverse=True)
    
    print()
    print("=" * 80)
    print(f"📊 TOTAL ARTICLES FOUND: {len(all_articles)}")
    print("=" * 80)
    print()
    
    if not all_articles:
        print("⚠️  No articles found in the last 7 days.")
        print("   Try expanding the date range or checking your API key.")
        return
    
    # Display articles
    for i, article in enumerate(all_articles, 1):
        print(f"\n{'='*80}")
        print(f"📰 ARTICLE {i}/{len(all_articles)}")
        print(f"{'='*80}")
        print()
        print(f"📌 Title: {article.get('title', 'N/A')}")
        print()
        print(f"📅 Published: {article.get('published_at', 'N/A')}")
        print(f"📰 Source: {article.get('source', 'N/A')}")
        print(f"✍️  Author: {article.get('author', 'N/A')}")
        print()
        print(f"🔗 URL: {article.get('url', 'N/A')}")
        print()
        
        # Show description/content
        content = article.get('content', '') or article.get('description', '')
        if content:
            print(f"📝 Summary:")
            print("-" * 80)
            # Truncate if too long
            if len(content) > 500:
                print(content[:500] + "...")
                print(f"\n[Read more at: {article.get('url', 'N/A')}]")
            else:
                print(content)
            print()
    
    print()
    print("=" * 80)
    print(f"✅ Displayed {len(all_articles)} latest articles")
    print("=" * 80)

if __name__ == "__main__":
    main()

