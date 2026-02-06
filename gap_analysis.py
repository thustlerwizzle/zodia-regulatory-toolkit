"""
Gap Analysis Module for comparing regulations with company policies
"""
from typing import Dict, List, Optional
from datetime import datetime
import json


class GapAnalyzer:
    """Analyzes gaps between regulatory requirements and company policies"""
    
    def __init__(self):
        self.regulatory_requirements = {}
        self.company_policies = {}
    
    def load_regulatory_requirements(self, regulatory_data: Dict) -> None:
        """Load regulatory requirements from research results"""
        self.regulatory_requirements = regulatory_data
    
    def load_company_policies(self, policies: Dict) -> None:
        """Load current company policies"""
        self.company_policies = policies
    
    def analyze_gaps(
        self, 
        regulatory_summary: str,
        current_policies: str,
        focus_areas: List[str] = None
    ) -> Dict:
        """
        Perform gap analysis between regulatory requirements and company policies
        
        Args:
            regulatory_summary: Summary of regulatory requirements
            current_policies: Current company policies text
            focus_areas: Specific areas to focus on (e.g., ["AML", "KYC", "Data Protection"])
        
        Returns:
            Dictionary containing gap analysis results
        """
        gaps = {
            "timestamp": datetime.now().isoformat(),
            "regulatory_areas_analyzed": focus_areas or [],
            "identified_gaps": [],
            "compliance_status": {},
            "recommendations": [],
            "priority_levels": {
                "critical": [],
                "high": [],
                "medium": [],
                "low": []
            }
        }
        
        # This would typically use an LLM to analyze the gap
        # For now, we'll structure it for LLM processing
        analysis_prompt = self._create_gap_analysis_prompt(
            regulatory_summary, 
            current_policies, 
            focus_areas
        )
        
        gaps["analysis_prompt"] = analysis_prompt
        
        return gaps
    
    def _create_gap_analysis_prompt(
        self, 
        regulatory_summary: str, 
        current_policies: str,
        focus_areas: List[str] = None
    ) -> str:
        """Create a prompt for LLM-based gap analysis"""
        focus_text = ""
        if focus_areas:
            focus_text = f"\nFocus Areas: {', '.join(focus_areas)}"
        
        prompt = f"""You are a regulatory compliance expert. Analyze the gaps between regulatory requirements and company policies.

REGULATORY REQUIREMENTS:
{regulatory_summary}

CURRENT COMPANY POLICIES:
{current_policies}
{focus_text}

Please provide a structured gap analysis that includes:
1. Identified Gaps: List specific gaps between regulations and policies
2. Compliance Status: For each regulatory requirement, indicate if it's met, partially met, or not met
3. Recommendations: Specific recommendations to address each gap
4. Priority Levels: Categorize gaps as Critical, High, Medium, or Low priority

Format your response as JSON with the following structure:
{{
    "identified_gaps": [
        {{
            "gap_id": "GAP-001",
            "regulatory_requirement": "Description of requirement",
            "current_policy_status": "Description of current policy",
            "gap_description": "What's missing",
            "priority": "critical|high|medium|low",
            "impact": "Description of impact if not addressed",
            "recommendation": "Specific recommendation"
        }}
    ],
    "compliance_status": {{
        "requirement_name": "met|partial|not_met"
    }},
    "summary": "Overall compliance summary"
}}
"""
        return prompt
    
    def categorize_gaps(self, gaps: List[Dict]) -> Dict[str, List[Dict]]:
        """Categorize gaps by priority level"""
        categorized = {
            "critical": [],
            "high": [],
            "medium": [],
            "low": []
        }
        
        for gap in gaps:
            priority = gap.get("priority", "medium").lower()
            if priority in categorized:
                categorized[priority].append(gap)
            else:
                categorized["medium"].append(gap)
        
        return categorized
    
    def generate_gap_report(self, gap_analysis: Dict) -> str:
        """Generate a human-readable gap analysis report"""
        report = f"""# Gap Analysis Report
Generated: {gap_analysis.get('timestamp', 'N/A')}

## Executive Summary
"""
        
        if "summary" in gap_analysis:
            report += f"{gap_analysis['summary']}\n\n"
        
        # Critical Gaps
        critical = gap_analysis.get("priority_levels", {}).get("critical", [])
        if critical:
            report += "## Critical Priority Gaps\n\n"
            for i, gap in enumerate(critical, 1):
                report += f"### Gap {i}: {gap.get('gap_id', f'GAP-{i:03d}')}\n"
                report += f"**Requirement:** {gap.get('regulatory_requirement', 'N/A')}\n\n"
                report += f"**Current Status:** {gap.get('current_policy_status', 'N/A')}\n\n"
                report += f"**Gap:** {gap.get('gap_description', 'N/A')}\n\n"
                report += f"**Impact:** {gap.get('impact', 'N/A')}\n\n"
                report += f"**Recommendation:** {gap.get('recommendation', 'N/A')}\n\n"
        
        # High Priority Gaps
        high = gap_analysis.get("priority_levels", {}).get("high", [])
        if high:
            report += "## High Priority Gaps\n\n"
            for i, gap in enumerate(high, 1):
                report += f"### Gap {i}: {gap.get('gap_id', f'GAP-{i:03d}')}\n"
                report += f"**Requirement:** {gap.get('regulatory_requirement', 'N/A')}\n\n"
                report += f"**Recommendation:** {gap.get('recommendation', 'N/A')}\n\n"
        
        # Compliance Status
        if "compliance_status" in gap_analysis:
            report += "## Compliance Status\n\n"
            for req, status in gap_analysis["compliance_status"].items():
                status_emoji = "✅" if status == "met" else "⚠️" if status == "partial" else "❌"
                report += f"{status_emoji} **{req}**: {status}\n"
        
        return report

