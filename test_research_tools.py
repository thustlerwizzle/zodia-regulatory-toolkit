"""
Test research tools with the new API key
"""
from research_tools import ResearchTools
from config import NEWSAPI_KEY

print("=" * 70)
print("Testing Research Tools with NewsAPI")
print("=" * 70)
print(f"\nCurrent NewsAPI Key: {NEWSAPI_KEY[:10]}...{NEWSAPI_KEY[-10:] if NEWSAPI_KEY else 'NOT SET'}")
print()

# Initialize research tools
print("🔧 Initializing ResearchTools...")
tools = ResearchTools()

if not tools.newsapi_client:
    print("❌ NewsAPI client not initialized - key may be missing")
else:
    print("✅ NewsAPI client initialized")
    print()
    
    # Test search
    print("🔍 Testing news search...")
    print("Query: cryptocurrency regulation")
    print()
    
    try:
        results = tools.search_news("cryptocurrency regulation", days=7)
        print(f"✅ Search successful!")
        print(f"📊 Found {len(results)} articles")
        print()
        
        if results:
            print("📰 Sample Articles:")
            print("-" * 70)
            for i, article in enumerate(results[:3], 1):
                print(f"\n{i}. {article.get('title', 'N/A')}")
                print(f"   Source: {article.get('source', 'N/A')}")
                print(f"   URL: {article.get('url', 'N/A')[:80]}...")
                print(f"   Published: {article.get('published_at', 'N/A')}")
        else:
            print("⚠️  No articles found (this might be normal if there are no recent articles)")
            
    except Exception as e:
        print(f"❌ Error during search: {str(e)}")
        import traceback
        traceback.print_exc()

print()
print("=" * 70)

