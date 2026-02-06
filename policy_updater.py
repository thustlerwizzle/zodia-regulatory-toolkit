"""
Policy and Standards Update Module
"""
from typing import Dict, List, Optional
from datetime import datetime
import json
import yaml
import os
from pathlib import Path


class PolicyUpdater:
    """Manages updates to company policies and standards based on regulatory analysis"""
    
    def __init__(self):
        self.policy_templates = {}
        self.update_history = []
    
    def generate_policy_updates(
        self,
        gap_analysis: Dict,
        current_policies: Dict,
        regulatory_summary: str
    ) -> Dict:
        """
        Generate policy updates based on gap analysis
        
        Args:
            gap_analysis: Results from gap analysis
            current_policies: Current company policies
            regulatory_summary: Summary of regulatory requirements
        
        Returns:
            Dictionary containing proposed policy updates
        """
        updates = {
            "timestamp": datetime.now().isoformat(),
            "proposed_updates": [],
            "new_policies": [],
            "modified_policies": [],
            "update_rationale": {},
            "implementation_priority": {}
        }
        
        # Extract gaps that require policy updates
        gaps = gap_analysis.get("identified_gaps", [])
        
        for gap in gaps:
            update = {
                "gap_id": gap.get("gap_id", ""),
                "policy_category": self._categorize_policy(gap),
                "current_policy": gap.get("current_policy_status", ""),
                "proposed_change": gap.get("recommendation", ""),
                "regulatory_basis": gap.get("regulatory_requirement", ""),
                "priority": gap.get("priority", "medium"),
                "impact": gap.get("impact", "")
            }
            updates["proposed_updates"].append(update)
            
            # Determine if this is a new policy or modification
            if "not addressed" in gap.get("current_policy_status", "").lower():
                updates["new_policies"].append(update)
            else:
                updates["modified_policies"].append(update)
        
        return updates
    
    def _categorize_policy(self, gap: Dict) -> str:
        """Categorize policy based on gap content"""
        requirement = gap.get("regulatory_requirement", "").lower()
        
        if any(term in requirement for term in ["aml", "kyc", "identity", "verification"]):
            return "AML/KYC"
        elif any(term in requirement for term in ["data", "privacy", "gdpr", "protection"]):
            return "Data Protection"
        elif any(term in requirement for term in ["risk", "assessment", "management"]):
            return "Risk Management"
        elif any(term in requirement for term in ["operational", "process", "procedure"]):
            return "Operational"
        elif any(term in requirement for term in ["legal", "contract", "agreement"]):
            return "Legal"
        else:
            return "Compliance"
    
    def create_policy_draft(
        self,
        policy_update: Dict,
        template: Optional[str] = None
    ) -> str:
        """Create a draft policy document based on update requirements"""
        prompt = f"""You are a policy writer. Create a comprehensive policy document based on the following requirements:

REGULATORY REQUIREMENT:
{policy_update.get('regulatory_basis', '')}

CURRENT POLICY STATUS:
{policy_update.get('current_policy', '')}

PROPOSED CHANGE:
{policy_update.get('proposed_change', '')}

POLICY CATEGORY: {policy_update.get('policy_category', 'Compliance')}

Create a professional policy document that includes:
1. Policy Title
2. Purpose and Scope
3. Definitions
4. Policy Statement
5. Procedures
6. Compliance Requirements
7. Review and Update Schedule
8. References to Regulatory Requirements

Format the policy in Markdown."""
        
        return prompt
    
    def generate_update_summary(self, updates: Dict) -> str:
        """Generate a summary of proposed policy updates"""
        summary = f"""# Policy Update Summary
Generated: {updates.get('timestamp', 'N/A')}

## Overview
This document summarizes proposed updates to company policies and standards based on regulatory gap analysis.

## New Policies Required
"""
        for policy in updates.get("new_policies", []):
            summary += f"\n### {policy.get('gap_id', 'N/A')}\n"
            summary += f"**Category:** {policy.get('policy_category', 'N/A')}\n"
            summary += f"**Priority:** {policy.get('priority', 'N/A')}\n"
            summary += f"**Regulatory Basis:** {policy.get('regulatory_basis', 'N/A')}\n"
            summary += f"**Proposed Change:** {policy.get('proposed_change', 'N/A')}\n"
        
        summary += "\n## Modified Policies\n"
        for policy in updates.get("modified_policies", []):
            summary += f"\n### {policy.get('gap_id', 'N/A')}\n"
            summary += f"**Category:** {policy.get('policy_category', 'N/A')}\n"
            summary += f"**Current Policy:** {policy.get('current_policy', 'N/A')}\n"
            summary += f"**Proposed Change:** {policy.get('proposed_change', 'N/A')}\n"
        
        return summary
    
    def save_policy_update(self, updates: Dict, filepath: str) -> None:
        """Save policy updates to a file"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(updates, f, indent=2, ensure_ascii=False)
    
    def track_update_history(self, update: Dict) -> None:
        """Track policy update history"""
        self.update_history.append({
            "timestamp": datetime.now().isoformat(),
            "update": update
        })
    
    def get_update_history(self) -> List[Dict]:
        """Get policy update history"""
        return self.update_history
    
    def implement_policies(
        self,
        policy_updates: Dict,
        llm=None,
        output_dir: str = None
    ) -> Dict:
        """
        Automatically implement policy recommendations by creating actual policy files
        
        Args:
            policy_updates: Policy updates dictionary
            llm: Language model for generating policy content
            output_dir: Directory to save policies (defaults to Desktop)
        
        Returns:
            Dictionary with implementation results
        """
        # Get desktop path
        if output_dir is None:
            desktop = Path.home() / "Desktop"
            output_dir = desktop / "Regulatory_Policies"
        else:
            output_dir = Path(output_dir)
        
        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)
        
        implementation_results = {
            "timestamp": datetime.now().isoformat(),
            "output_directory": str(output_dir),
            "implemented_policies": [],
            "failed_policies": [],
            "files_created": []
        }
        
        # Implement all policy updates
        all_updates = policy_updates.get("proposed_updates", [])
        
        for update in all_updates:
            try:
                # Generate full policy document if we have LLM
                policy_content = None
                if llm and update.get("policy_draft"):
                    policy_content = update["policy_draft"]
                elif llm:
                    # Generate policy if we don't have a draft yet
                    draft_prompt = self.create_policy_draft(update)
                    from langchain_core.messages import HumanMessage, SystemMessage
                    messages = [
                        SystemMessage(content="You are a professional policy writer. Create complete, ready-to-use policy documents."),
                        HumanMessage(content=draft_prompt)
                    ]
                    response = llm.invoke(messages)
                    policy_content = response.content
                else:
                    # Create basic policy structure without LLM
                    policy_content = self._create_basic_policy(update)
                
                # Create filename
                category = update.get("policy_category", "Compliance").replace("/", "_")
                gap_id = update.get("gap_id", f"POLICY_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
                filename = f"{category}_{gap_id}.md"
                filepath = output_dir / filename
                
                # Add metadata header
                full_content = f"""---
Policy ID: {gap_id}
Category: {update.get('policy_category', 'Compliance')}
Priority: {update.get('priority', 'medium')}
Regulatory Basis: {update.get('regulatory_basis', 'N/A')[:100]}
Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Status: Implemented
---

{policy_content}
"""
                
                # Save policy file
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(full_content)
                
                implementation_results["implemented_policies"].append({
                    "gap_id": gap_id,
                    "category": update.get("policy_category"),
                    "priority": update.get("priority"),
                    "filepath": str(filepath),
                    "filename": filename
                })
                implementation_results["files_created"].append(str(filepath))
                
            except Exception as e:
                implementation_results["failed_policies"].append({
                    "gap_id": update.get("gap_id", "unknown"),
                    "error": str(e)
                })
        
        # Create implementation summary
        summary_file = output_dir / "IMPLEMENTATION_SUMMARY.md"
        summary_content = f"""# Policy Implementation Summary

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Overview
This document summarizes the automatic implementation of policy recommendations based on regulatory gap analysis.

## Implementation Results

### Successfully Implemented Policies: {len(implementation_results['implemented_policies'])}

"""
        for policy in implementation_results["implemented_policies"]:
            summary_content += f"""
#### {policy['gap_id']}
- **Category:** {policy['category']}
- **Priority:** {policy['priority']}
- **File:** `{policy['filename']}`

"""
        
        if implementation_results["failed_policies"]:
            summary_content += f"""
### Failed Implementations: {len(implementation_results['failed_policies'])}

"""
            for failed in implementation_results["failed_policies"]:
                summary_content += f"- **{failed['gap_id']}:** {failed['error']}\n"
        
        summary_content += f"""
## Files Created

All policy files have been saved to:
`{output_dir}`

Total files created: {len(implementation_results['files_created'])}
"""
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(summary_content)
        
        implementation_results["summary_file"] = str(summary_file)
        
        return implementation_results
    
    def _create_basic_policy(self, update: Dict) -> str:
        """Create a basic policy structure without LLM"""
        return f"""# {update.get('policy_category', 'Compliance')} Policy

## Policy ID: {update.get('gap_id', 'N/A')}

### Regulatory Requirement
{update.get('regulatory_basis', 'N/A')}

### Current Status
{update.get('current_policy', 'Not addressed')}

### Recommended Implementation
{update.get('proposed_change', 'N/A')}

### Priority
{update.get('priority', 'medium').upper()}

### Impact
{update.get('impact', 'N/A')}

---

**Note:** This is an automatically generated policy template. Please review and customize as needed.

**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

