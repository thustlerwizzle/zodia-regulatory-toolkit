"""
Full Stablecoin Regulation Analysis - ALL Jurisdictions
Comprehensive analysis across all 300+ countries and territories
With automatic retry and robust error handling
"""
import sys
import io

# Fix Windows console encoding for Unicode
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)

import warnings
warnings.filterwarnings('ignore', category=FutureWarning)

import json
import os
from datetime import datetime
from pathlib import Path
from config import JURISDICTIONS, DEEPSEEK_API_KEY
import time
import traceback

# Create results directory
RESULTS_DIR = Path("stablecoin_analysis_all_jurisdictions")
RESULTS_DIR.mkdir(exist_ok=True)

# Progress tracking file
PROGRESS_FILE = RESULTS_DIR / "progress.json"
SUMMARY_FILE = RESULTS_DIR / "FULL_ANALYSIS_SUMMARY.md"

# Retry settings
MAX_RETRIES = 3
RETRY_DELAY = 30  # seconds

def load_progress():
    """Load progress from previous run"""
    if PROGRESS_FILE.exists():
        try:
            with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {
        "completed": [],
        "failed": [],
        "start_time": datetime.now().isoformat(),
        "last_update": None
    }

def save_progress(progress):
    """Save progress"""
    progress["last_update"] = datetime.now().isoformat()
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump(progress, f, indent=2, ensure_ascii=False)

def create_agent_with_retry():
    """Create agent with retry logic"""
    from regulatory_agent import RegulatoryAgent
    
    for attempt in range(MAX_RETRIES):
        try:
            agent = RegulatoryAgent()
            return agent
        except Exception as e:
            print(f"   Attempt {attempt + 1}/{MAX_RETRIES} failed: {e}")
            if attempt < MAX_RETRIES - 1:
                print(f"   Retrying in {RETRY_DELAY} seconds...")
                time.sleep(RETRY_DELAY)
            else:
                raise

def analyze_jurisdiction_with_retry(agent, jurisdiction, progress):
    """Analyze a single jurisdiction with retry logic"""
    print(f"\n{'='*80}")
    print(f"Analyzing: {jurisdiction}")
    print(f"Progress: {len(progress['completed'])}/{len(JURISDICTIONS)} completed")
    print(f"{'='*80}")
    
    for attempt in range(MAX_RETRIES):
        try:
            # Run analysis
            results = agent.run(
                query="stablecoin regulation",
                jurisdiction=jurisdiction,
                current_policies=""
            )
            
            # Save individual result
            safe_name = jurisdiction.replace(" ", "_").replace("/", "_")
            result_file = RESULTS_DIR / f"{safe_name}_analysis.json"
            
            result_data = {
                "jurisdiction": jurisdiction,
                "timestamp": datetime.now().isoformat(),
                "regulatory_summary": results.get("regulatory_summary", ""),
                "gap_analysis": results.get("gap_analysis", {}),
                "policy_updates": results.get("policy_updates", {}),
                "sources_count": len(results.get("sources", [])),
                "sources": results.get("sources", [])[:10],
                "has_policy_implementation": bool(results.get("policy_implementation", {}).get("files_created")),
                "report": results.get("report", "")
            }
            
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(result_data, f, indent=2, ensure_ascii=False)
            
            # Save markdown report
            if results.get("report"):
                report_file = RESULTS_DIR / f"{safe_name}_report.md"
                with open(report_file, 'w', encoding='utf-8') as f:
                    f.write(results["report"])
            
            # Update progress
            progress["completed"].append({
                "jurisdiction": jurisdiction,
                "timestamp": datetime.now().isoformat(),
                "result_file": str(result_file),
                "gaps_critical": len(results.get("gap_analysis", {}).get("priority_levels", {}).get("critical", [])),
                "gaps_high": len(results.get("gap_analysis", {}).get("priority_levels", {}).get("high", [])),
                "sources": len(results.get("sources", []))
            })
            
            save_progress(progress)
            
            print(f"✅ Completed: {jurisdiction}")
            print(f"   Sources: {result_data['sources_count']}")
            
            return True
            
        except Exception as e:
            error_msg = str(e)
            print(f"   ⚠️ Attempt {attempt + 1}/{MAX_RETRIES} failed: {error_msg[:100]}")
            
            if attempt < MAX_RETRIES - 1:
                print(f"   Retrying in {RETRY_DELAY} seconds...")
                time.sleep(RETRY_DELAY)
            else:
                print(f"❌ Failed: {jurisdiction} after {MAX_RETRIES} attempts")
                progress["failed"].append({
                    "jurisdiction": jurisdiction,
                    "timestamp": datetime.now().isoformat(),
                    "error": error_msg
                })
                save_progress(progress)
                return False

def generate_summary(progress):
    """Generate comprehensive summary report"""
    print("\n" + "="*80)
    print("GENERATING SUMMARY REPORT")
    print("="*80)
    
    completed = progress.get("completed", [])
    failed = progress.get("failed", [])
    
    summary = f"""# Full Stablecoin Regulation Analysis - ALL Jurisdictions

**Analysis Date:** {progress.get('start_time', 'N/A')}
**Last Update:** {progress.get('last_update', 'N/A')}
**Total Jurisdictions:** {len(JURISDICTIONS)}
**Completed:** {len(completed)}
**Failed:** {len(failed)}
**Remaining:** {len(JURISDICTIONS) - len(completed) - len(failed)}

---

## Executive Summary

This comprehensive analysis covers stablecoin regulation across **{len(JURISDICTIONS)} jurisdictions** including all UN member states and major territories.

### Completion Status

- ✅ **Completed:** {len(completed)} jurisdictions ({len(completed)/len(JURISDICTIONS)*100:.1f}%)
- ❌ **Failed:** {len(failed)} jurisdictions
- ⏳ **Remaining:** {len(JURISDICTIONS) - len(completed) - len(failed)} jurisdictions

---

## Results by Jurisdiction

"""
    
    # Group by region/priority
    major_jurisdictions = ["United States", "European Union", "United Kingdom", "China", "Japan", "Singapore", "Switzerland", "Canada", "Australia"]
    
    summary += "### Major Jurisdictions\n\n"
    for item in completed:
        if item["jurisdiction"] in major_jurisdictions:
            summary += f"#### {item['jurisdiction']}\n"
            summary += f"- **Critical Gaps:** {item.get('gaps_critical', 0)}\n"
            summary += f"- **High Priority Gaps:** {item.get('gaps_high', 0)}\n"
            summary += f"- **Sources Found:** {item.get('sources', 0)}\n"
            summary += f"- **Report:** `{item.get('result_file', 'N/A')}`\n\n"
    
    summary += "\n### All Completed Jurisdictions\n\n"
    summary += "| Jurisdiction | Critical Gaps | High Gaps | Sources | Status |\n"
    summary += "|--------------|---------------|-----------|---------|--------|\n"
    
    for item in completed:
        summary += f"| {item['jurisdiction']} | {item.get('gaps_critical', 0)} | {item.get('gaps_high', 0)} | {item.get('sources', 0)} | ✅ |\n"
    
    if failed:
        summary += "\n### Failed Jurisdictions\n\n"
        summary += "| Jurisdiction | Error |\n"
        summary += "|--------------|-------|\n"
        for item in failed:
            error = item.get('error', 'Unknown error')[:100]
            summary += f"| {item['jurisdiction']} | {error} |\n"
    
    # Statistics
    total_critical = sum(item.get('gaps_critical', 0) for item in completed)
    total_high = sum(item.get('gaps_high', 0) for item in completed)
    total_sources = sum(item.get('sources', 0) for item in completed)
    
    summary += f"""
---

## Statistics

- **Total Critical Gaps Identified:** {total_critical}
- **Total High Priority Gaps:** {total_high}
- **Total Sources Collected:** {total_sources}
- **Average Gaps per Jurisdiction:** {total_critical/len(completed) if completed else 0:.1f} critical, {total_high/len(completed) if completed else 0:.1f} high

---

## Data Files

All individual jurisdiction analyses are saved in:
- **Directory:** `{RESULTS_DIR}/`
- **Format:** JSON files (`*_analysis.json`) and Markdown reports (`*_report.md`)
- **Progress Tracking:** `progress.json`

---

*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
    
    with open(SUMMARY_FILE, 'w', encoding='utf-8') as f:
        f.write(summary)
    
    print(f"✅ Summary saved to: {SUMMARY_FILE}")

def main():
    """Main execution with robust error handling"""
    print("="*80)
    print("FULL STABLECOIN REGULATION ANALYSIS - ALL JURISDICTIONS")
    print("="*80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    if not DEEPSEEK_API_KEY:
        print("❌ ERROR: DEEPSEEK_API_KEY not found in .env file")
        return
    
    # Load progress first to check if resuming
    progress = load_progress()
    completed_jurisdictions = {item["jurisdiction"] for item in progress.get("completed", [])}
    failed_jurisdictions = {item["jurisdiction"] for item in progress.get("failed", [])}
    remaining_count = len(JURISDICTIONS) - len(completed_jurisdictions) - len(failed_jurisdictions)
    
    print(f"📊 Total Jurisdictions: {len(JURISDICTIONS)}")
    print(f"⏱️  Estimated Time: {remaining_count * 6 / 60:.1f} hours (at ~6 min per jurisdiction)")
    print(f"💾 Results will be saved to: {RESULTS_DIR}/")
    
    if len(completed_jurisdictions) > 0:
        print(f"\n📋 Resuming from previous run:")
        print(f"   ✅ Already completed: {len(completed_jurisdictions)}")
        print(f"   ❌ Previously failed: {len(failed_jurisdictions)}")
        print(f"   ⏳ Remaining: {remaining_count}")
        print("\n🔄 Auto-continuing from previous progress...\n")
    else:
        print("\n⚠️  WARNING: This will take MANY HOURS to complete!")
        print("   You can stop and resume later - progress is saved.\n")
        response = input("Continue? (yes/no): ").strip().lower()
        if response != 'yes':
            print("Cancelled.")
            return
    
    # Initialize agent with retry
    print("🔄 Initializing Regulatory Agent...")
    try:
        agent = create_agent_with_retry()
        print("✅ Agent initialized\n")
    except Exception as e:
        print(f"❌ Failed to initialize agent after {MAX_RETRIES} attempts: {e}")
        return
    
    # Process each jurisdiction
    start_time = time.time()
    remaining = [j for j in JURISDICTIONS if j not in completed_jurisdictions and j not in failed_jurisdictions]
    
    print(f"🚀 Starting analysis of {len(remaining)} jurisdictions...\n")
    
    consecutive_failures = 0
    max_consecutive_failures = 5
    
    for i, jurisdiction in enumerate(remaining, 1):
        elapsed = time.time() - start_time
        avg_time = elapsed / i if i > 0 else 0
        remaining_time = avg_time * (len(remaining) - i)
        
        print(f"\n[{i}/{len(remaining)}] Estimated remaining: {remaining_time/3600:.1f} hours")
        
        success = analyze_jurisdiction_with_retry(agent, jurisdiction, progress)
        
        if success:
            consecutive_failures = 0
        else:
            consecutive_failures += 1
            if consecutive_failures >= max_consecutive_failures:
                print(f"\n⚠️ {max_consecutive_failures} consecutive failures. Reinitializing agent...")
                try:
                    agent = create_agent_with_retry()
                    consecutive_failures = 0
                    print("✅ Agent reinitialized")
                except Exception as e:
                    print(f"❌ Failed to reinitialize agent: {e}")
                    print("Stopping analysis...")
                    break
        
        # Small delay to avoid rate limiting
        time.sleep(3)
        
        # Generate summary every 10 jurisdictions
        if i % 10 == 0:
            generate_summary(progress)
            print(f"\n💾 Progress saved. {len(progress['completed'])}/{len(JURISDICTIONS)} completed")
    
    # Final summary
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE!")
    print("="*80)
    generate_summary(progress)
    
    total_time = time.time() - start_time
    print(f"\n⏱️  Total time: {total_time/3600:.2f} hours")
    print(f"📊 Results saved to: {RESULTS_DIR}/")
    print(f"📄 Summary: {SUMMARY_FILE}")

if __name__ == "__main__":
    while True:
        try:
            main()
            break  # Exit if completed normally
        except KeyboardInterrupt:
            print("\n\n⚠️  Analysis interrupted by user.")
            print("💾 Progress has been saved. You can resume later by running this script again.")
            break
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            traceback.print_exc()
            print("\n🔄 Restarting in 60 seconds... (Press Ctrl+C to stop)")
            try:
                time.sleep(60)
                print("🔄 Restarting analysis...")
            except KeyboardInterrupt:
                print("\n⚠️  Stopped by user.")
                break
