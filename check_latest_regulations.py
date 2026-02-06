"""
Quick script to check latest regulations using the regulatory agent
"""
import sys
from regulatory_agent import RegulatoryAgent
from config import DEEPSEEK_API_KEY

def main():
    """Run agent to get latest regulations"""
    # Check if API key is set
    if not DEEPSEEK_API_KEY:
        print("❌ Error: DEEPSEEK_API_KEY not found in .env file")
        print("Please set DEEPSEEK_API_KEY in your .env file")
        sys.exit(1)
    
    print("🔍 Regulatory Analysis Agent - Latest Regulations Check")
    print("=" * 70)
    
    # Initialize agent
    print("\n🚀 Initializing agent...")
    try:
        agent = RegulatoryAgent()
    except Exception as e:
        print(f"❌ Error initializing agent: {str(e)}")
        sys.exit(1)
    
    # Run analysis for latest regulations
    query = "latest cryptocurrency and digital asset regulations 2024 2025"
    jurisdiction = ""  # Global analysis
    
    print(f"\n📊 Query: {query}")
    print("🌍 Scope: Global (all jurisdictions)")
    print("\n⏳ Running regulatory analysis...")
    print("This may take a few minutes...\n")
    
    try:
        results = agent.run(
            query=query,
            jurisdiction=jurisdiction,
            current_policies=""
        )
        
        # Display results
        print("\n" + "=" * 70)
        print("📋 LATEST REGULATORY DEVELOPMENTS")
        print("=" * 70)
        
        # Regulatory Summary
        if results.get("regulatory_summary"):
            print("\n## 📋 Regulatory Requirements Summary")
            print("-" * 70)
            print(results["regulatory_summary"])
            print()
        
        # Sources
        if results.get("sources"):
            sources = results["sources"]
            print("\n## 📚 Sources Found")
            print("-" * 70)
            print(f"Total sources: {len(sources)}\n")
            for i, source in enumerate(sources[:10], 1):  # Show first 10
                print(f"{i}. {source.get('title', 'N/A')}")
                print(f"   🔗 {source.get('url', 'N/A')}")
                if source.get('published_at'):
                    print(f"   📅 {source.get('published_at')}")
                print()
        
        # Full Report
        if results.get("report"):
            from datetime import datetime
            filename = f"regulatory_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(results["report"])
            print(f"\n✅ Full report saved to: {filename}")
        
        # Errors
        if results.get("error"):
            print(f"\n⚠️  Warning: {results['error']}")
        
        print("\n" + "=" * 70)
        print("✅ Analysis Complete!")
        print("=" * 70)
        
        return results
        
    except Exception as e:
        print(f"\n❌ Error during analysis: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

