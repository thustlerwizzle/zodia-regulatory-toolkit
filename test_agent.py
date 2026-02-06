"""
Quick test script for the regulatory agent
"""
from regulatory_agent import RegulatoryAgent
from config import DEEPSEEK_API_KEY

def test_agent():
    """Test the agent with a simple query"""
    if not DEEPSEEK_API_KEY:
        print("❌ Error: DEEPSEEK_API_KEY not found")
        return
    
    print("🔍 Testing Regulatory Analysis Agent")
    print("=" * 50)
    
    # Initialize agent
    print("\n🚀 Initializing agent...")
    agent = RegulatoryAgent()
    
    # Test with a simple query
    print("📊 Running test analysis...")
    print("Query: 'stablecoin regulation'")
    print("This may take a few minutes...\n")
    
    try:
        results = agent.run(
            query="stablecoin regulation",
            jurisdiction="",
            current_policies=""
        )
        
        print("\n" + "=" * 50)
        print("✅ TEST RESULTS")
        print("=" * 50)
        
        if results.get("error"):
            print(f"⚠️  Error: {results['error']}")
        else:
            print("✅ Analysis completed successfully!")
            if results.get("regulatory_summary"):
                print(f"\n📋 Regulatory Summary: {len(results['regulatory_summary'])} characters")
            if results.get("sources"):
                print(f"📚 Sources found: {len(results['sources'])}")
            if results.get("report"):
                print(f"📄 Report generated: {len(results['report'])} characters")
        
        print("\n" + "=" * 50)
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_agent()

