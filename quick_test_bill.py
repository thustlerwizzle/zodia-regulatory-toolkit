"""
Quick test to see what news articles are found for "bill" query
"""
from research_tools import ResearchTools

print("=" * 80)
print("🔍 Quick Test: What news articles are found for 'bill'?")
print("=" * 80)

tools = ResearchTools()

# Test different bill-related queries
queries = [
    "bill",
    "crypto bill",
    "cryptocurrency bill",
    "regulation bill"
]

all_articles = []
seen_urls = set()

for query in queries:
    print(f"\n🔍 Searching: '{query}'...")
    try:
        articles = tools.search_news(query, days=7)
        print(f"   Found {len(articles)} articles")
        
        for article in articles:
            url = article.get('url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                all_articles.append(article)
                print(f"   ✓ {article.get('title', 'N/A')[:60]}...")
    except Exception as e:
        print(f"   Error: {str(e)}")

print(f"\n" + "=" * 80)
print(f"📊 TOTAL UNIQUE ARTICLES: {len(all_articles)}")
print("=" * 80)

if all_articles:
    print("\n📰 Sample Articles Found:")
    print("-" * 80)
    for i, article in enumerate(all_articles[:10], 1):
        print(f"\n{i}. {article.get('title', 'N/A')}")
        print(f"   Source: {article.get('source', 'N/A')}")
        print(f"   Date: {article.get('published_at', 'N/A')}")
        print(f"   URL: {article.get('url', 'N/A')}")
        if article.get('content'):
            print(f"   Content: {article.get('content', '')[:200]}...")
else:
    print("\n⚠️  No articles found. The query might be too generic or no recent news matches.")




