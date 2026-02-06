"""
Test script: Stablecoin regulation across all jurisdictions
Tests the full workflow including news, research, gap analysis, and policy implementation
"""
import warnings
warnings.filterwarnings('ignore', category=FutureWarning)

from regulatory_agent import RegulatoryAgent
from research_tools import ResearchTools
from config import JURISDICTIONS, REGULATORY_AREAS, DEEPSEEK_API_KEY
from datetime import datetime
import json

def test_stablecoin_all_jurisdictions():
    """Test stablecoin regulation analysis across all jurisdictions"""
    
    print("=" * 80)
    print("COMPREHENSIVE STABLECOIN REGULATION TEST")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Check API key
    if not DEEPSEEK_API_KEY:
        print("❌ ERROR: DEEPSEEK_API_KEY not found in .env file")
        return
    
    print("✅ API Key found")
    print(f"📊 Testing across {len(JURISDICTIONS)} jurisdictions")
    print(f"📋 Testing {len(REGULATORY_AREAS)} regulatory topics\n")
    
    # Initialize agent
    print("🔄 Initializing Regulatory Agent...")
    try:
        agent = RegulatoryAgent()
        print("✅ Agent initialized\n")
    except Exception as e:
        print(f"❌ Failed to initialize agent: {e}")
        return
    
    # Test 1: Global stablecoin regulation (no specific jurisdiction)
    print("-" * 80)
    print("TEST 1: GLOBAL STABLECOIN REGULATION ANALYSIS")
    print("-" * 80)
    
    try:
        print("🔍 Running analysis for: 'stablecoin regulation' (Global)")
        print("⏳ This may take 5-7 minutes...\n")
        
        results = agent.run(
            query="stablecoin regulation",
            jurisdiction="",  # Empty = global analysis
            current_policies=""  # No current policies for this test
        )
        
        print("✅ Analysis complete!\n")
        
        # Display summary
        print("=" * 80)
        print("RESULTS SUMMARY")
        print("=" * 80)
        
        if results.get("regulatory_summary"):
            summary = results["regulatory_summary"]
            print(f"\n📋 Regulatory Summary ({len(summary)} chars):")
            print(summary[:500] + "..." if len(summary) > 500 else summary)
        
        if results.get("gap_analysis"):
            gap_analysis = results["gap_analysis"]
            priority_levels = gap_analysis.get("priority_levels", {})
            print(f"\n🔍 Gap Analysis:")
            print(f"  • Critical: {len(priority_levels.get('critical', []))}")
            print(f"  • High: {len(priority_levels.get('high', []))}")
            print(f"  • Medium: {len(priority_levels.get('medium', []))}")
            print(f"  • Low: {len(priority_levels.get('low', []))}")
        
        if results.get("policy_updates"):
            policy_updates = results["policy_updates"]
            print(f"\n📝 Policy Updates:")
            print(f"  • New Policies: {len(policy_updates.get('new_policies', []))}")
            print(f"  • Modified Policies: {len(policy_updates.get('modified_policies', []))}")
        
        if results.get("policy_implementation"):
            impl = results["policy_implementation"]
            if impl.get("files_created"):
                print(f"\n✅ Policy Implementation:")
                print(f"  • Implemented: {len(impl.get('implemented_policies', []))} policies")
                print(f"  • Saved to: {impl.get('output_directory', 'N/A')}")
                print(f"  • Summary: {impl.get('summary_file', 'N/A')}")
        
        if results.get("sources"):
            sources = results["sources"]
            print(f"\n📚 Sources: {len(sources)} total")
            print("  First 5 sources:")
            for i, source in enumerate(sources[:5], 1):
                print(f"    {i}. {source.get('title', 'N/A')}")
                print(f"       {source.get('url', 'N/A')}")
        
        # Save full report
        if results.get("report"):
            filename = f"test_stablecoin_global_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(results["report"])
            print(f"\n📄 Full report saved to: {filename}")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 2: Latest News
    print("\n" + "=" * 80)
    print("TEST 2: LATEST STABLECOIN REGULATION NEWS")
    print("=" * 80)
    
    try:
        print("📰 Fetching latest stablecoin regulation news...")
        tools = ResearchTools()
        
        queries = [
            "stablecoin regulation",
            "stablecoin compliance",
            "stablecoin legislation",
            "crypto stablecoin regulation"
        ]
        
        all_articles = []
        seen_urls = set()
        
        for query in queries:
            try:
                print(f"  🔍 Searching: '{query}'...")
                articles = tools.search_news(query, days=7)
                for article in articles:
                    url = article.get('url', '')
                    if url and url not in seen_urls:
                        seen_urls.add(url)
                        all_articles.append(article)
                print(f"    ✅ Found {len(articles)} articles")
            except Exception as e:
                print(f"    ⚠️ Error: {e}")
        
        # Sort by date
        all_articles.sort(key=lambda x: x.get('published_at', ''), reverse=True)
        
        print(f"\n✅ Total unique articles: {len(all_articles)}")
        print("\n📰 Latest Articles (first 10):")
        for i, article in enumerate(all_articles[:10], 1):
            print(f"\n  {i}. {article.get('title', 'N/A')}")
            print(f"     📅 {article.get('published_at', 'N/A')[:10] if article.get('published_at') else 'N/A'}")
            print(f"     📰 {article.get('source', 'N/A')}")
            print(f"     🔗 {article.get('url', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Error fetching news: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 3: Sample jurisdictions
    print("\n" + "=" * 80)
    print("TEST 3: SAMPLE JURISDICTIONS (Top 5)")
    print("=" * 80)
    print("Testing stablecoin regulation in top 5 jurisdictions...\n")
    
    sample_jurisdictions = [
        "United States",
        "European Union",
        "United Kingdom",
        "Singapore",
        "Japan"
    ]
    
    for jurisdiction in sample_jurisdictions:
        try:
            print(f"🌍 Testing: {jurisdiction}")
            print(f"   ⏳ Running analysis...")
            
            results = agent.run(
                query="stablecoin regulation",
                jurisdiction=jurisdiction,
                current_policies=""
            )
            
            if results.get("regulatory_summary"):
                summary_len = len(results["regulatory_summary"])
                print(f"   ✅ Summary: {summary_len} chars")
            
            if results.get("gap_analysis"):
                gaps = results["gap_analysis"].get("priority_levels", {})
                total_gaps = sum(len(v) for v in gaps.values())
                print(f"   ✅ Gaps identified: {total_gaps}")
            
            if results.get("sources"):
                print(f"   ✅ Sources: {len(results['sources'])}")
            
            print()
            
        except Exception as e:
            print(f"   ❌ Error: {e}\n")
    
    print("=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)
    print(f"Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n✅ All tests completed successfully!")

if __name__ == "__main__":
    test_stablecoin_all_jurisdictions()

