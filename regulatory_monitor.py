"""
Live Regulatory Monitoring System
Tracks crypto, stablecoin, and digital asset regulations across all jurisdictions
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json
import os
from pathlib import Path
from research_tools import ResearchTools
from regulatory_agent import RegulatoryAgent
from policy_updater import PolicyUpdater
from config import JURISDICTIONS, REGULATORY_AREAS


class RegulatoryMonitor:
    """Monitors regulatory changes and tracks revisions"""
    
    def __init__(self, data_dir: str = "regulatory_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.revisions_dir = self.data_dir / "revisions"
        self.revisions_dir.mkdir(exist_ok=True)
        self.notifications_dir = self.data_dir / "notifications"
        self.notifications_dir.mkdir(exist_ok=True)
        self.research_tools = ResearchTools()
        self.agent = None
        self.policy_updater = PolicyUpdater()
    
    def initialize_agent(self):
        """Initialize the regulatory agent"""
        if self.agent is None:
            try:
                self.agent = RegulatoryAgent()
            except Exception as e:
                print(f"Warning: Could not initialize agent: {e}")
    
    def get_regulatory_snapshot_file(self, jurisdiction: str, topic: str) -> Path:
        """Get file path for regulatory snapshot"""
        safe_jurisdiction = jurisdiction.replace(" ", "_").replace("/", "_")
        safe_topic = topic.replace(" ", "_").replace("/", "_")
        filename = f"{safe_jurisdiction}_{safe_topic}.json"
        return self.data_dir / filename
    
    def load_regulatory_snapshot(self, jurisdiction: str, topic: str) -> Optional[Dict]:
        """Load previous regulatory snapshot"""
        snapshot_file = self.get_regulatory_snapshot_file(jurisdiction, topic)
        if snapshot_file.exists():
            try:
                with open(snapshot_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading snapshot: {e}")
        return None
    
    def save_regulatory_snapshot(self, jurisdiction: str, topic: str, data: Dict):
        """Save current regulatory snapshot"""
        snapshot_file = self.get_regulatory_snapshot_file(jurisdiction, topic)
        data['last_updated'] = datetime.now().isoformat()
        with open(snapshot_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def compare_regulations(self, old_data: Dict, new_data: Dict) -> Dict:
        """Compare old and new regulatory data to detect changes"""
        changes = {
            "timestamp": datetime.now().isoformat(),
            "changes_detected": False,
            "new_regulations": [],
            "modified_regulations": [],
            "removed_regulations": [],
            "summary_changes": [],
            "gap_changes": []
        }
        
        old_summary = old_data.get("regulatory_summary", "")
        new_summary = new_data.get("regulatory_summary", "")
        
        if old_summary != new_summary:
            changes["changes_detected"] = True
            changes["summary_changes"].append({
                "type": "summary_update",
                "old_length": len(old_summary),
                "new_length": len(new_summary),
                "change_percentage": abs(len(new_summary) - len(old_summary)) / max(len(old_summary), 1) * 100
            })
        
        # Compare gap analysis
        old_gaps = old_data.get("gap_analysis", {}).get("identified_gaps", [])
        new_gaps = new_data.get("gap_analysis", {}).get("identified_gaps", [])
        
        if len(old_gaps) != len(new_gaps):
            changes["changes_detected"] = True
            changes["gap_changes"].append({
                "type": "gap_count_change",
                "old_count": len(old_gaps),
                "new_count": len(new_gaps),
                "difference": len(new_gaps) - len(old_gaps)
            })
        
        # Compare policy updates
        old_policies = old_data.get("policy_updates", {}).get("proposed_updates", [])
        new_policies = new_data.get("policy_updates", {}).get("proposed_updates", [])
        
        if len(old_policies) != len(new_policies):
            changes["changes_detected"] = True
            changes["new_regulations"].append({
                "type": "policy_count_change",
                "old_count": len(old_policies),
                "new_count": len(new_policies)
            })
        
        return changes
    
    def create_revision(self, jurisdiction: str, topic: str, changes: Dict, old_data: Dict, new_data: Dict):
        """Create a revision record"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_jurisdiction = jurisdiction.replace(" ", "_").replace("/", "_")
        safe_topic = topic.replace(" ", "_").replace("/", "_")
        revision_file = self.revisions_dir / f"{safe_jurisdiction}_{safe_topic}_{timestamp}.json"
        
        revision = {
            "timestamp": datetime.now().isoformat(),
            "jurisdiction": jurisdiction,
            "topic": topic,
            "changes": changes,
            "old_data_summary": {
                "regulatory_summary_length": len(old_data.get("regulatory_summary", "")),
                "gap_count": len(old_data.get("gap_analysis, {}").get("identified_gaps", [])),
                "policy_count": len(old_data.get("policy_updates", {}).get("proposed_updates", []))
            },
            "new_data_summary": {
                "regulatory_summary_length": len(new_data.get("regulatory_summary", "")),
                "gap_count": len(new_data.get("gap_analysis", {}).get("identified_gaps", [])),
                "policy_count": len(new_data.get("policy_updates", {}).get("proposed_updates", []))
            }
        }
        
        with open(revision_file, 'w', encoding='utf-8') as f:
            json.dump(revision, f, indent=2, ensure_ascii=False)
        
        return revision_file
    
    def create_notification(self, jurisdiction: str, topic: str, changes: Dict):
        """Create a notification about regulatory changes"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        notification_file = self.notifications_dir / f"notification_{timestamp}.md"
        
        notification = f"""# Regulatory Change Notification

**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Jurisdiction:** {jurisdiction}
**Topic:** {topic}

## Changes Detected

"""
        
        if changes.get("summary_changes"):
            notification += "### Regulatory Summary Changes\n"
            for change in changes["summary_changes"]:
                notification += f"- Summary updated: {change.get('change_percentage', 0):.1f}% change\n"
        
        if changes.get("gap_changes"):
            notification += "\n### Gap Analysis Changes\n"
            for change in changes["gap_changes"]:
                notification += f"- Gap count changed: {change.get('old_count', 0)} → {change.get('new_count', 0)}\n"
        
        if changes.get("new_regulations"):
            notification += "\n### New Regulations\n"
            for reg in changes["new_regulations"]:
                notification += f"- {reg.get('type', 'Unknown')}\n"
        
        notification += f"""
## Action Required

Please review the updated regulations and policy recommendations.

**Revision File:** Saved in revisions folder
**Policy Updates:** Check Desktop/Regulatory_Policies/ for updated policies

---
Generated by Regulatory Analysis Agent
"""
        
        with open(notification_file, 'w', encoding='utf-8') as f:
            f.write(notification)
        
        return notification_file
    
    def monitor_regulation(self, jurisdiction: str, topic: str) -> Dict:
        """
        Monitor a specific regulation and detect changes
        
        Args:
            jurisdiction: Jurisdiction to monitor
            topic: Regulatory topic to monitor
            
        Returns:
            Dictionary with monitoring results
        """
        if not self.agent:
            self.initialize_agent()
        
        if not self.agent:
            return {
                "error": "Agent not initialized",
                "success": False
            }
        
        # Load previous snapshot
        old_data = self.load_regulatory_snapshot(jurisdiction, topic)
        
        # Run new analysis
        try:
            new_data = self.agent.run(
                query=topic,
                jurisdiction=jurisdiction,
                current_policies=""
            )
            
            # Save new snapshot
            self.save_regulatory_snapshot(jurisdiction, topic, new_data)
            
            # Compare if we have old data
            if old_data:
                changes = self.compare_regulations(old_data, new_data)
                
                if changes.get("changes_detected"):
                    # Create revision
                    revision_file = self.create_revision(jurisdiction, topic, changes, old_data, new_data)
                    
                    # Create notification
                    notification_file = self.create_notification(jurisdiction, topic, changes)
                    
                    # Auto-update policies if changes detected
                    if new_data.get("policy_updates"):
                        try:
                            implementation = self.policy_updater.implement_policies(
                                policy_updates=new_data["policy_updates"],
                                llm=self.agent.llm
                            )
                            new_data["policy_implementation"] = implementation
                        except Exception as e:
                            print(f"Error implementing policies: {e}")
                    
                    return {
                        "success": True,
                        "changes_detected": True,
                        "changes": changes,
                        "revision_file": str(revision_file),
                        "notification_file": str(notification_file),
                        "data": new_data
                    }
                else:
                    return {
                        "success": True,
                        "changes_detected": False,
                        "message": "No changes detected",
                        "data": new_data
                    }
            else:
                # First time monitoring - no comparison
                return {
                    "success": True,
                    "changes_detected": False,
                    "message": "Initial snapshot created",
                    "data": new_data
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def monitor_all_jurisdictions(self, topics: List[str] = None) -> Dict:
        """
        Monitor regulations across all jurisdictions
        
        Args:
            topics: List of topics to monitor (defaults to REGULATORY_AREAS)
            
        Returns:
            Dictionary with monitoring results for all jurisdictions
        """
        if topics is None:
            topics = REGULATORY_AREAS
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "jurisdictions_monitored": len(JURISDICTIONS),
            "topics_monitored": len(topics),
            "results": {}
        }
        
        for jurisdiction in JURISDICTIONS:
            results["results"][jurisdiction] = {}
            for topic in topics:
                print(f"Monitoring: {jurisdiction} - {topic}")
                result = self.monitor_regulation(jurisdiction, topic)
                results["results"][jurisdiction][topic] = result
        
        return results
    
    def get_revision_history(self, jurisdiction: str = None, topic: str = None) -> List[Dict]:
        """Get revision history"""
        revisions = []
        
        for revision_file in self.revisions_dir.glob("*.json"):
            try:
                with open(revision_file, 'r', encoding='utf-8') as f:
                    revision = json.load(f)
                    
                    if jurisdiction and revision.get("jurisdiction") != jurisdiction:
                        continue
                    if topic and revision.get("topic") != topic:
                        continue
                    
                    revisions.append(revision)
            except Exception as e:
                print(f"Error reading revision {revision_file}: {e}")
        
        # Sort by timestamp (newest first)
        revisions.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return revisions
    
    def get_recent_notifications(self, limit: int = 10) -> List[str]:
        """Get recent notification files"""
        notifications = sorted(
            self.notifications_dir.glob("*.md"),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        return [str(n) for n in notifications[:limit]]

