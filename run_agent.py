"""
Direct execution script for Regulatory Analysis Agent
Run without Streamlit interface
"""
import sys
from regulatory_agent import RegulatoryAgent
from config import DEEPSEEK_API_KEY


def main():
    """Main execution function"""
    # Check if API key is set
    if not DEEPSEEK_API_KEY:
        print("❌ Error: DEEPSEEK_API_KEY not found in .env file")
        print("Please set DEEPSEEK_API_KEY in your .env file")
        print("Get your API key from: https://platform.deepseek.com/api_keys")
        sys.exit(1)
    
    print("🔍 Regulatory Analysis Agent")
    print("=" * 50)
    
    # Get user input
    print("\nEnter your regulatory analysis query:")
    query = input("> ").strip()
    
    if not query:
        print("❌ Error: Query cannot be empty")
        sys.exit(1)
    
    print("\nEnter jurisdiction (optional, press Enter to skip):")
    jurisdiction = input("> ").strip()
    
    print("\nEnter current company policies (optional, press Enter to skip):")
    print("(You can paste multiple lines, press Enter twice when done)")
    policies = []
    while True:
        line = input()
        if line == "":
            if policies:  # If we have content and get empty line, break
                break
            else:  # If first line is empty, skip policies
                break
        policies.append(line)
    
    current_policies = "\n".join(policies) if policies else ""
    
    # Initialize agent
    print("\n🚀 Initializing agent...")
    agent = RegulatoryAgent()
    
    # Run analysis
    print("📊 Running regulatory analysis...")
    print("This may take a few minutes...\n")
    
    try:
        results = agent.run(
            query=query,
            jurisdiction=jurisdiction,
            current_policies=current_policies
        )
        
        # Display results
        print("\n" + "=" * 50)
        print("📋 REGULATORY ANALYSIS RESULTS")
        print("=" * 50)
        
        # Regulatory Summary
        if results.get("regulatory_summary"):
            print("\n## Regulatory Requirements Summary")
            print("-" * 50)
            print(results["regulatory_summary"])
        
        # Gap Analysis
        if results.get("gap_analysis"):
            gap_analysis = results["gap_analysis"]
            print("\n## Gap Analysis")
            print("-" * 50)
            
            priority_levels = gap_analysis.get("priority_levels", {})
            if priority_levels:
                print(f"\nCritical Gaps: {len(priority_levels.get('critical', []))}")
                print(f"High Priority Gaps: {len(priority_levels.get('high', []))}")
                print(f"Medium Priority Gaps: {len(priority_levels.get('medium', []))}")
                print(f"Low Priority Gaps: {len(priority_levels.get('low', []))}")
                
                # Show critical gaps
                critical = priority_levels.get("critical", [])
                if critical:
                    print("\n### Critical Priority Gaps:")
                    for i, gap in enumerate(critical[:3], 1):  # Show first 3
                        print(f"\n{i}. {gap.get('gap_id', f'GAP-{i:03d}')}")
                        print(f"   Requirement: {gap.get('regulatory_requirement', 'N/A')[:100]}...")
                        print(f"   Recommendation: {gap.get('recommendation', 'N/A')[:100]}...")
        
        # Policy Updates
        if results.get("policy_updates"):
            policy_updates = results["policy_updates"]
            print("\n## Policy Updates")
            print("-" * 50)
            print(f"New Policies Required: {len(policy_updates.get('new_policies', []))}")
            print(f"Policies to Modify: {len(policy_updates.get('modified_policies', []))}")
        
        # Sources
        if results.get("sources"):
            sources = results["sources"]
            print(f"\n## Sources ({len(sources)} total)")
            print("-" * 50)
            for i, source in enumerate(sources[:5], 1):  # Show first 5
                print(f"{i}. {source.get('title', 'N/A')}")
                print(f"   {source.get('url', 'N/A')}")
        
        # Full Report
        if results.get("report"):
            print("\n" + "=" * 50)
            print("📄 Full Report Generated")
            print("=" * 50)
            
            # Save report to file
            from datetime import datetime
            filename = f"regulatory_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(results["report"])
            print(f"\n✅ Report saved to: {filename}")
        
        # Errors
        if results.get("error"):
            print(f"\n⚠️  Warning: {results['error']}")
        
        print("\n" + "=" * 50)
        print("✅ Analysis Complete!")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ Error during analysis: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

