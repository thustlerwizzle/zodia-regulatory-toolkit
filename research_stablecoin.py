"""
Research Stablecoin Regulations
Quick research script for stablecoin regulation analysis
"""
import warnings
warnings.filterwarnings('ignore', category=FutureWarning)

from regulatory_agent import RegulatoryAgent
from research_tools import ResearchTools
from config import DEEPSEEK_API_KEY
from datetime import datetime

def research_stablecoin():
    """Research stablecoin regulations"""
    
    print("=" * 80)
    print("STABLECOIN REGULATION RESEARCH")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    if not DEEPSEEK_API_KEY:
        print("❌ ERROR: DEEPSEEK_API_KEY not found in .env file")
        return
    
    # Initialize agent
    print("🔄 Initializing Regulatory Agent...")
    try:
        agent = RegulatoryAgent()
        print("✅ Agent initialized\n")
    except Exception as e:
        print(f"❌ Failed to initialize agent: {e}")
        return
    
    # Run research
    print("-" * 80)
    print("RUNNING STABLECOIN REGULATION RESEARCH")
    print("-" * 80)
    print("Query: 'stablecoin regulation'")
    print("Scope: Global (all jurisdictions)")
    print("⏳ This may take 5-7 minutes...\n")
    
    try:
        results = agent.run(
            query="stablecoin regulation",
            jurisdiction="",  # Global analysis
            current_policies=""
        )
        
        print("✅ Research complete!\n")
        
        # Display results
        print("=" * 80)
        print("RESEARCH RESULTS")
        print("=" * 80)
        
        # Regulatory Summary
        if results.get("regulatory_summary"):
            print("\n📋 REGULATORY SUMMARY:")
            print("-" * 80)
            summary = results["regulatory_summary"]
            print(summary)
            print()
        
        # Gap Analysis
        if results.get("gap_analysis"):
            gap_analysis = results["gap_analysis"]
            priority_levels = gap_analysis.get("priority_levels", {})
            print("\n🔍 GAP ANALYSIS:")
            print("-" * 80)
            print(f"Critical Gaps: {len(priority_levels.get('critical', []))}")
            print(f"High Priority Gaps: {len(priority_levels.get('high', []))}")
            print(f"Medium Priority Gaps: {len(priority_levels.get('medium', []))}")
            print(f"Low Priority Gaps: {len(priority_levels.get('low', []))}")
            
            # Show critical gaps
            critical = priority_levels.get("critical", [])
            if critical:
                print("\nCritical Priority Gaps:")
                for i, gap in enumerate(critical[:5], 1):
                    print(f"\n  {i}. {gap.get('gap_id', f'GAP-{i:03d}')}")
                    print(f"     Requirement: {gap.get('regulatory_requirement', 'N/A')[:150]}...")
                    print(f"     Recommendation: {gap.get('recommendation', 'N/A')[:150]}...")
            print()
        
        # Policy Updates
        if results.get("policy_updates"):
            policy_updates = results["policy_updates"]
            print("\n📝 POLICY UPDATES:")
            print("-" * 80)
            print(f"New Policies Required: {len(policy_updates.get('new_policies', []))}")
            print(f"Policies to Modify: {len(policy_updates.get('modified_policies', []))}")
            print()
        
        # Policy Implementation
        if results.get("policy_implementation") and results["policy_implementation"].get("files_created"):
            impl = results["policy_implementation"]
            print("\n✅ POLICY IMPLEMENTATION:")
            print("-" * 80)
            print(f"Implemented: {len(impl.get('implemented_policies', []))} policies")
            print(f"Saved to: {impl.get('output_directory', 'N/A')}")
            print(f"Summary: {impl.get('summary_file', 'N/A')}")
            print("\nImplemented Policies:")
            for policy in impl.get("implemented_policies", []):
                print(f"  • {policy.get('gap_id', 'N/A')} - {policy.get('filename', 'N/A')}")
            print()
        
        # Sources
        if results.get("sources"):
            sources = results["sources"]
            print("\n📚 SOURCES:")
            print("-" * 80)
            print(f"Total Sources: {len(sources)}")
            print("\nTop 10 Sources:")
            for i, source in enumerate(sources[:10], 1):
                print(f"\n  {i}. {source.get('title', 'N/A')}")
                print(f"     🔗 {source.get('url', 'N/A')}")
                if source.get('published_at'):
                    print(f"     📅 {source.get('published_at', '')[:10]}")
            print()
        
        # Save report
        if results.get("report"):
            filename = f"stablecoin_research_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(results["report"])
            print(f"\n📄 Full report saved to: {filename}")
        
        print("\n" + "=" * 80)
        print("RESEARCH COMPLETE")
        print("=" * 80)
        print(f"Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        print(f"\n❌ Error during research: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    research_stablecoin()


