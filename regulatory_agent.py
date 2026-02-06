"""
Regulatory Analysis Agent using LangGraph
"""
from typing import Dict, List, TypedDict, Annotated
from datetime import datetime
import json
from langgraph.graph import StateGraph, END
from langchain_deepseek import ChatDeepSeek
try:
    from langchain_core.messages import HumanMessage, SystemMessage
except ImportError:
    from langchain.schema import HumanMessage, SystemMessage
from research_tools import ResearchTools
from gap_analysis import GapAnalyzer
from policy_updater import PolicyUpdater
from config import LLM_MODEL, LLM_TEMPERATURE, DEEPSEEK_API_KEY  # This import enables LangSmith tracing


class AgentState(TypedDict):
    """State for the regulatory analysis agent"""
    query: str
    jurisdiction: str
    topic: str
    research_results: Dict
    regulatory_summary: str
    current_policies: str
    gap_analysis: Dict
    policy_updates: Dict
    policy_implementation: Dict
    sources: List[Dict]
    report: str
    error: str


class RegulatoryAgent:
    """Main agent for regulatory analysis, gap analysis, and policy updates"""
    
    def __init__(self):
        self.llm = ChatDeepSeek(
            model=LLM_MODEL,
            temperature=LLM_TEMPERATURE,
            max_tokens=None,
            timeout=None,
            max_retries=2
        ) if DEEPSEEK_API_KEY else None
        self.research_tools = ResearchTools()
        self.gap_analyzer = GapAnalyzer()
        self.policy_updater = PolicyUpdater()
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("research", self._research_node)
        workflow.add_node("summarize", self._summarize_node)
        workflow.add_node("analyze_gaps", self._gap_analysis_node)
        workflow.add_node("update_policies", self._policy_update_node)
        workflow.add_node("implement_policies", self._implement_policies_node)
        workflow.add_node("generate_report", self._report_node)
        
        # Set entry point
        workflow.set_entry_point("research")
        
        # Add edges
        workflow.add_edge("research", "summarize")
        workflow.add_edge("summarize", "analyze_gaps")
        workflow.add_edge("analyze_gaps", "update_policies")
        workflow.add_edge("update_policies", "implement_policies")
        workflow.add_edge("implement_policies", "generate_report")
        workflow.add_edge("generate_report", END)
        
        return workflow.compile()
    
    def _research_node(self, state: AgentState) -> AgentState:
        """Perform research on regulatory requirements"""
        try:
            query = state.get("query", state.get("topic", ""))
            jurisdiction = state.get("jurisdiction", "")
            
            results = self.research_tools.search_regulatory_updates(
                topic=query,
                jurisdiction=jurisdiction if jurisdiction else None
            )
            
            # Extract sources
            sources = self.research_tools.get_all_sources(results)
            
            state["research_results"] = results
            state["sources"] = sources
            
        except Exception as e:
            state["error"] = f"Research error: {str(e)}"
        
        return state
    
    def _summarize_node(self, state: AgentState) -> AgentState:
        """Summarize regulatory requirements"""
        try:
            results = state.get("research_results", {})
            
            # Combine all research results
            all_content = []
            for source_type in ["news"]:
                for result in results.get(source_type, []):
                    content = f"Title: {result.get('title', '')}\n"
                    content += f"Content: {result.get('content', '')}\n"
                    content += f"URL: {result.get('url', '')}\n"
                    all_content.append(content)
            
            combined_content = "\n\n---\n\n".join(all_content)
            
            # Use LLM to summarize if available
            if self.llm:
                # Check if we have any content to summarize
                if not combined_content or len(combined_content.strip()) < 50:
                    summary = f"""Regulatory Research Summary

Note: Limited research results were obtained. This may be due to:
- API key issues (check your .env file)
- Rate limiting
- Network connectivity issues

Query: {results.get('query', 'N/A')}

The agent will proceed with analysis based on available information and LLM knowledge.
"""
                else:
                    prompt = f"""You are a regulatory compliance expert. Summarize the following research findings about cryptocurrency, blockchain, and digital asset regulations.

Focus on:
- Key regulatory requirements
- Compliance obligations
- Recent regulatory changes
- Jurisdiction-specific requirements
- Enforcement actions or guidance

Research Findings:
{combined_content[:8000]}  # Limit content to avoid token limits

Provide a comprehensive summary in structured format."""
                    
                    messages = [
                        SystemMessage(content="You are an expert regulatory compliance analyst specializing in cryptocurrency and digital assets."),
                        HumanMessage(content=prompt)
                    ]
                    
                    response = self.llm.invoke(messages)
                    summary = response.content
            else:
                # Fallback summary
                if not combined_content or len(combined_content.strip()) < 50:
                    summary = "Limited research results available. Please check API keys in .env file."
                else:
                    summary = f"Regulatory Research Summary\n\nFound {len(all_content)} sources.\n\nKey findings from research:\n{combined_content[:2000]}"
            
            state["regulatory_summary"] = summary
            
        except Exception as e:
            state["error"] = f"Summarization error: {str(e)}"
            state["regulatory_summary"] = "Error generating summary"
        
        return state
    
    def _gap_analysis_node(self, state: AgentState) -> AgentState:
        """Perform gap analysis"""
        try:
            regulatory_summary = state.get("regulatory_summary", "")
            current_policies = state.get("current_policies", "No current policies provided.")
            
            # Perform gap analysis
            gap_analysis = self.gap_analyzer.analyze_gaps(
                regulatory_summary=regulatory_summary,
                current_policies=current_policies
            )
            
            # Use LLM to process gap analysis if available
            if self.llm:
                analysis_prompt = gap_analysis.get("analysis_prompt", "")
                if analysis_prompt:
                    messages = [
                        SystemMessage(content="You are a regulatory compliance expert performing gap analysis."),
                        HumanMessage(content=analysis_prompt)
                    ]
                    
                    response = self.llm.invoke(messages)
                    result_text = response.content
                    
                    # Try to parse JSON from response
                    try:
                        # Extract JSON from markdown code blocks if present
                        if "```json" in result_text:
                            json_start = result_text.find("```json") + 7
                            json_end = result_text.find("```", json_start)
                            result_text = result_text[json_start:json_end].strip()
                        elif "```" in result_text:
                            json_start = result_text.find("```") + 3
                            json_end = result_text.find("```", json_start)
                            result_text = result_text[json_start:json_end].strip()
                        
                        parsed_result = json.loads(result_text)
                        gap_analysis.update(parsed_result)
                        
                        # Categorize gaps
                        if "identified_gaps" in parsed_result:
                            gap_analysis["priority_levels"] = self.gap_analyzer.categorize_gaps(
                                parsed_result["identified_gaps"]
                            )
                    except json.JSONDecodeError:
                        # If JSON parsing fails, store the text response
                        gap_analysis["llm_analysis"] = result_text
            
            state["gap_analysis"] = gap_analysis
            
        except Exception as e:
            state["error"] = f"Gap analysis error: {str(e)}"
            state["gap_analysis"] = {}
        
        return state
    
    def _policy_update_node(self, state: AgentState) -> AgentState:
        """Generate policy updates"""
        try:
            gap_analysis = state.get("gap_analysis", {})
            regulatory_summary = state.get("regulatory_summary", "")
            current_policies = state.get("current_policies", {})
            
            policy_updates = self.policy_updater.generate_policy_updates(
                gap_analysis=gap_analysis,
                current_policies=current_policies,
                regulatory_summary=regulatory_summary
            )
            
            # Generate policy drafts using LLM if available
            if self.llm and "proposed_updates" in policy_updates:
                for update in policy_updates["proposed_updates"]:
                    if update.get("priority") in ["critical", "high"]:
                        draft_prompt = self.policy_updater.create_policy_draft(update)
                        messages = [
                            SystemMessage(content="You are a professional policy writer."),
                            HumanMessage(content=draft_prompt)
                        ]
                        response = self.llm.invoke(messages)
                        update["policy_draft"] = response.content
            
            state["policy_updates"] = policy_updates
            
        except Exception as e:
            state["error"] = f"Policy update error: {str(e)}"
            state["policy_updates"] = {}
        
        return state
    
    def _implement_policies_node(self, state: AgentState) -> AgentState:
        """Automatically implement policy recommendations"""
        try:
            policy_updates = state.get("policy_updates", {})
            
            if not policy_updates or not policy_updates.get("proposed_updates"):
                state["policy_implementation"] = {
                    "message": "No policy updates to implement",
                    "files_created": []
                }
                return state
            
            # Generate policy drafts for all updates if not already done
            if self.llm and "proposed_updates" in policy_updates:
                for update in policy_updates["proposed_updates"]:
                    if not update.get("policy_draft"):
                        draft_prompt = self.policy_updater.create_policy_draft(update)
                        messages = [
                            SystemMessage(content="You are a professional policy writer. Create complete, ready-to-use policy documents."),
                            HumanMessage(content=draft_prompt)
                        ]
                        response = self.llm.invoke(messages)
                        update["policy_draft"] = response.content
            
            # Implement policies (save to desktop)
            implementation_results = self.policy_updater.implement_policies(
                policy_updates=policy_updates,
                llm=self.llm
            )
            
            state["policy_implementation"] = implementation_results
            
        except Exception as e:
            state["error"] = f"Policy implementation error: {str(e)}"
            state["policy_implementation"] = {
                "error": str(e),
                "files_created": []
            }
        
        return state
    
    def _report_node(self, state: AgentState) -> AgentState:
        """Generate final report"""
        try:
            report_sections = []
            
            # Executive Summary
            report_sections.append("# Regulatory Analysis Report")
            report_sections.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            # Research Summary
            regulatory_summary = state.get("regulatory_summary", "")
            if regulatory_summary:
                report_sections.append("## Regulatory Requirements Summary\n")
                report_sections.append(regulatory_summary)
                report_sections.append("\n")
            
            # Gap Analysis
            gap_analysis = state.get("gap_analysis", {})
            if gap_analysis:
                gap_report = self.gap_analyzer.generate_gap_report(gap_analysis)
                report_sections.append(gap_report)
                report_sections.append("\n")
            
            # Policy Updates
            policy_updates = state.get("policy_updates", {})
            if policy_updates:
                update_summary = self.policy_updater.generate_update_summary(policy_updates)
                report_sections.append(update_summary)
                report_sections.append("\n")
            
            # Policy Implementation
            policy_implementation = state.get("policy_implementation", {})
            if policy_implementation and policy_implementation.get("files_created"):
                report_sections.append("## Policy Implementation\n")
                report_sections.append(f"✅ **Automatically implemented {len(policy_implementation.get('implemented_policies', []))} policies**\n")
                report_sections.append(f"📁 **Saved to:** {policy_implementation.get('output_directory', 'N/A')}\n")
                report_sections.append(f"📄 **Summary file:** {policy_implementation.get('summary_file', 'N/A')}\n\n")
                
                if policy_implementation.get("implemented_policies"):
                    report_sections.append("### Implemented Policies:\n")
                    for policy in policy_implementation["implemented_policies"]:
                        report_sections.append(f"- **{policy.get('gap_id', 'N/A')}** ({policy.get('category', 'N/A')}) - {policy.get('filename', 'N/A')}\n")
                report_sections.append("\n")
            
            # Sources
            sources = state.get("sources", [])
            if sources:
                report_sections.append("## Sources\n")
                for i, source in enumerate(sources, 1):
                    report_sections.append(f"{i}. [{source.get('title', 'N/A')}]({source.get('url', '')})")
                    report_sections.append(f"   Source: {source.get('source_type', 'N/A')}")
                report_sections.append("\n")
            
            # Error handling
            if state.get("error"):
                report_sections.append(f"\n## Errors\n{state.get('error')}")
            
            state["report"] = "\n".join(report_sections)
            
        except Exception as e:
            state["error"] = f"Report generation error: {str(e)}"
            state["report"] = f"Error generating report: {str(e)}"
        
        return state
    
    def run(self, query: str, jurisdiction: str = "", current_policies: str = "") -> Dict:
        """Run the complete regulatory analysis workflow"""
        initial_state = {
            "query": query,
            "topic": query,
            "jurisdiction": jurisdiction,
            "current_policies": current_policies,
            "research_results": {},
            "regulatory_summary": "",
            "gap_analysis": {},
            "policy_updates": {},
            "policy_implementation": {},
            "sources": [],
            "report": "",
            "error": ""
        }
        
        try:
            final_state = self.workflow.invoke(initial_state)
            return final_state
        except Exception as e:
            return {
                **initial_state,
                "error": f"Workflow error: {str(e)}",
                "report": f"Error: {str(e)}"
            }

