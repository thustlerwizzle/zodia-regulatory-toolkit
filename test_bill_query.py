"""
Test the agent with "bill" query to see specific results
"""
import sys
from regulatory_agent import RegulatoryAgent
from config import DEEPSEEK_API_KEY

def main():
    """Run agent with 'bill' query"""
    if not DEEPSEEK_API_KEY:
        print("❌ Error: DEEPSEEK_API_KEY not found")
        sys.exit(1)
    
    print("=" * 80)
    print("🔍 Testing Agent with Query: 'bill'")
    print("=" * 80)
    
    # Initialize agent
    print("\n🚀 Initializing agent...")
    agent = RegulatoryAgent()
    
    # Run with "bill" query
    query = "bill"
    jurisdiction = ""
    
    print(f"\n📊 Query: '{query}'")
    print("🌍 Scope: Global")
    print("\n⏳ Running analysis... This will show specific results, not generic summaries.\n")
    
    try:
        results = agent.run(
            query=query,
            jurisdiction=jurisdiction,
            current_policies=""
        )
        
        print("\n" + "=" * 80)
        print("📋 SPECIFIC RESULTS FOR 'BILL' QUERY")
        print("=" * 80)
        
        # Show research results first
        if results.get("research_results"):
            research = results["research_results"]
            news_articles = research.get("news", [])
            print(f"\n📰 NEWS ARTICLES FOUND: {len(news_articles)}")
            print("-" * 80)
            for i, article in enumerate(news_articles[:10], 1):
                print(f"\n{i}. {article.get('title', 'N/A')}")
                print(f"   Source: {article.get('source', 'N/A')}")
                print(f"   Published: {article.get('published_at', 'N/A')}")
                print(f"   URL: {article.get('url', 'N/A')}")
                if article.get('content'):
                    print(f"   Preview: {article.get('content', '')[:150]}...")
        
        # Regulatory Summary
        if results.get("regulatory_summary"):
            print("\n" + "=" * 80)
            print("📋 REGULATORY SUMMARY")
            print("=" * 80)
            print(results["regulatory_summary"])
        
        # Sources
        if results.get("sources"):
            sources = results["sources"]
            print(f"\n📚 SOURCES ({len(sources)} total)")
            print("-" * 80)
            for i, source in enumerate(sources[:15], 1):
                print(f"{i}. {source.get('title', 'N/A')}")
                print(f"   🔗 {source.get('url', 'N/A')}")
        
        # Save report
        if results.get("report"):
            from datetime import datetime
            filename = f"regulatory_report_bill_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(results["report"])
            print(f"\n✅ Full report saved to: {filename}")
        
        print("\n" + "=" * 80)
        print("✅ Analysis Complete!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()




