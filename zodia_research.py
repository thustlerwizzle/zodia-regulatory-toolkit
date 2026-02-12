"""
Zodia Markets Regulatory Research Engine
Performs deep regulatory research specifically tailored for Zodia Markets' business model.
Walks through each business activity and maps to relevant regulations.
Covers reverse solicitation, direct market access, and cross-border advisory.
Only returns enacted/enforced/final regulations.
"""

import json
import time
from typing import Dict, List, Optional
from datetime import datetime
from langchain_deepseek import ChatDeepSeek
try:
    from langchain_core.messages import HumanMessage, SystemMessage
except ImportError:
    from langchain.schema import HumanMessage, SystemMessage

from research_tools import ResearchTools
from config import DEEPSEEK_API_KEY, LLM_MODEL, LLM_TEMPERATURE
from zodia_config import (
    COMPANY_NAME,
    COMPANY_DESCRIPTION,
    COMPANY_ENTITY_TYPE,
    ZODIA_REGISTERED_JURISDICTIONS,
    ZODIA_EU_MICA_JURISDICTIONS,
    ZODIA_BUSINESS_ACTIVITIES,
    ZODIA_SERVICES,
    ZODIA_REGULATORY_FOCUS,
    REGULATION_STATUS_FILTER,
    REGULATION_STATUS_EXCLUDE,
    ZODIA_REPORT_SECTIONS,
    ZODIA_LICENSED_ENTITIES_CONTEXT
)


class ZodiaResearchEngine:
    """
    Research engine designed for Zodia Markets regulatory analysis.
    Uses DeepSeek LLM + NewsAPI to produce structured regulatory intelligence.
    Walks through each Zodia business activity and maps to relevant regulations.
    """

    def __init__(self):
        self.llm = ChatDeepSeek(
            model=LLM_MODEL,
            temperature=LLM_TEMPERATURE,
            max_tokens=None,
            timeout=120,
            max_retries=3
        ) if DEEPSEEK_API_KEY else None

        self.research_tools = ResearchTools()
        self.results_cache = {}

    def research_jurisdiction(
        self,
        jurisdiction: str,
        include_news: bool = True,
        progress_callback=None
    ) -> Dict:
        """
        Perform comprehensive regulatory research for a single jurisdiction.
        Maps each Zodia business activity to relevant local regulations.
        """
        start_time = datetime.now()

        if progress_callback:
            progress_callback(f"Researching {jurisdiction}...")

        # Step 1: Gather news
        news_articles = []
        if include_news:
            news_articles = self._fetch_news(jurisdiction, progress_callback)

        # Step 2: Check registration status
        registration_info = ZODIA_REGISTERED_JURISDICTIONS.get(jurisdiction, None)

        # Step 3: Generate structured report via DeepSeek
        if progress_callback:
            progress_callback(f"Analyzing {jurisdiction} regulations for Zodia's business activities...")

        report = self._generate_structured_report(
            jurisdiction=jurisdiction,
            news_articles=news_articles,
            registration_info=registration_info
        )

        # Step 4: Compile result
        result = {
            "jurisdiction": jurisdiction,
            "timestamp": datetime.now().isoformat(),
            "duration_seconds": (datetime.now() - start_time).total_seconds(),
            "is_registered": registration_info is not None,
            "registration_info": registration_info,
            "news_articles_found": len(news_articles),
            "news_articles": news_articles[:10],
            "report": report,
            "status": "success"
        }

        self.results_cache[jurisdiction] = result
        return result

    def research_all_registered_jurisdictions(self, progress_callback=None) -> Dict:
        """Research all jurisdictions where Zodia is registered."""
        results = {}
        jurisdictions = list(ZODIA_REGISTERED_JURISDICTIONS.keys())

        for i, jurisdiction in enumerate(jurisdictions, 1):
            if progress_callback:
                progress_callback(f"[{i}/{len(jurisdictions)}] {jurisdiction}")
            try:
                results[jurisdiction] = self.research_jurisdiction(
                    jurisdiction, progress_callback=progress_callback
                )
            except Exception as e:
                results[jurisdiction] = {
                    "jurisdiction": jurisdiction, "status": "error", "error": str(e)
                }
            if i < len(jurisdictions):
                time.sleep(2)

        return results

    def _fetch_news(self, jurisdiction: str, progress_callback=None) -> List[Dict]:
        """Fetch relevant news for a jurisdiction."""
        all_articles = []
        seen_urls = set()

        queries = [
            f"VASP regulation {jurisdiction}",
            f"crypto brokerage regulation {jurisdiction}",
            f"stablecoin regulation {jurisdiction}",
            f"digital asset exchange licensing {jurisdiction}"
        ]

        for query in queries:
            try:
                articles = self.research_tools.search_news(query, days=30)
                for article in articles:
                    url = article.get("url", "")
                    if url and url not in seen_urls:
                        seen_urls.add(url)
                        all_articles.append(article)
            except Exception as e:
                if progress_callback:
                    progress_callback(f"  News warning: {str(e)[:60]}")

        all_articles.sort(key=lambda x: x.get("published_at", ""), reverse=True)
        return all_articles[:20]

    def _generate_structured_report(
        self,
        jurisdiction: str,
        news_articles: List[Dict],
        registration_info: Optional[Dict]
    ) -> Dict:
        """
        Use DeepSeek to generate a structured regulatory report.
        Walks through each Zodia business activity and maps to local regulations.
        """
        if not self.llm:
            return self._generate_fallback_report(jurisdiction, news_articles, registration_info)

        # News context
        news_context = ""
        if news_articles:
            news_items = []
            for a in news_articles[:10]:
                news_items.append(
                    f"- {a.get('title', 'N/A')} ({a.get('published_at', 'N/A')[:10]})\n"
                    f"  {a.get('content', '')[:200]}"
                )
            news_context = "\n".join(news_items)
        else:
            news_context = "No recent news articles found."

        # Registration context
        if registration_info:
            reg_context = (
                f"ZODIA IS REGISTERED in {jurisdiction}:\n"
                f"- Entity: {registration_info.get('entity', 'N/A')}\n"
                f"- Regulator: {registration_info.get('regulator', 'N/A')}\n"
                f"- License: {registration_info.get('license_type', 'N/A')}\n"
                f"- Reference: {registration_info.get('reference', 'N/A')}\n"
                f"- Granted: {registration_info.get('date_granted', 'N/A')}\n"
                f"- Scope: {registration_info.get('scope', 'N/A')}"
            )
        else:
            reg_context = f"Zodia Markets is NOT registered in {jurisdiction}."

        # EU/MiCA note
        mica_note = ""
        if jurisdiction in ZODIA_EU_MICA_JURISDICTIONS:
            mica_note = (
                f"\nIMPORTANT: {jurisdiction} is an EU/EEA member. Under MiCA, "
                "Zodia may passport from Ireland once CASP-authorized. Analyze availability."
            )

        # Business activities context
        activities_text = "\n".join(
            f"  {i+1}. {act['name']}: {act['description']}"
            for i, act in enumerate(ZODIA_BUSINESS_ACTIVITIES.values())
        )
        services_text = "\n".join(f"  - {s}" for s in ZODIA_SERVICES)

        # Section descriptions
        sections_desc = "\n".join(
            f"  - **{key}**: {desc}" for key, desc in ZODIA_REPORT_SECTIONS.items()
        )

        prompt = f"""You are a senior regulatory compliance analyst and cross-border legal advisor. Prepare a regulatory intelligence report for **Zodia Markets** focused ONLY on regulations that DIRECTLY affect its specific business activities.

===========================================================================
ZODIA MARKETS - WHAT THE BUSINESS ACTUALLY DOES
===========================================================================
{COMPANY_DESCRIPTION}

SPECIFIC BUSINESS ACTIVITIES (map each to local regulations):
{activities_text}

SERVICES:
{services_text}

Entity type: {COMPANY_ENTITY_TYPE}

===========================================================================
ZODIA'S LICENSING FOOTPRINT (ONLY 4 JURISDICTIONS)
===========================================================================
{ZODIA_LICENSED_ENTITIES_CONTEXT}

===========================================================================
STATUS IN {jurisdiction.upper()}
===========================================================================
{reg_context}
{mica_note}

===========================================================================
RECENT NEWS
===========================================================================
{news_context}

===========================================================================
YOUR TASK - WALK THROUGH EACH BUSINESS ACTIVITY
===========================================================================

Analyze {jurisdiction}'s regulations ONLY as they relate to Zodia's actual business. Do NOT include generic crypto regulations that don't touch Zodia's activities.

Walk through EACH of Zodia's business activities:

1. OTC BROKERAGE: What license does Zodia need to broker OTC digital asset trades in {jurisdiction}? Cite the specific law/regulation.

2. ELECTRONIC EXCHANGE: What license for operating an electronic matching engine / trading platform for digital assets? MTF/OTF/market operator rules?

3. FIAT-TO-CRYPTO: What regulations govern fiat-to-crypto conversion? Payment services / money transmission license needed?

4. NON-CUSTODIAL MODEL: How does {jurisdiction} regulate custody delegation? Rules for non-custodial brokers using third-party custodians?

5. INSTITUTIONAL-ONLY: Does {jurisdiction} have lighter rules for serving ONLY institutional/professional clients vs retail?

6. REVERSE SOLICITATION: Does {jurisdiction} allow reverse solicitation? If a {jurisdiction} institutional client approaches Zodia ON THEIR OWN INITIATIVE, can Zodia serve them WITHOUT a local license? What are the EXACT conditions? Is this in statute, regulation, or guidance? What are the practical limitations?

7. DIRECT MARKET ACCESS: Can Zodia provide its trading platform directly to {jurisdiction} clients from UK/Ireland/ADGM/Jersey without local presence? Rules?

8. CROSS-BORDER: Which Zodia entity (UK, Ireland, ADGM, Jersey) is best positioned to serve a {jurisdiction} client? Why?

ONLY include ENACTED, ENFORCED, FINAL, IN FORCE regulations (as of February 2026).

---

**Format as JSON with these keys:**
{{
    "summary": "...",
    "high_level_risk_points": ["risk 1", "risk 2", ...],
    "regulatory_framework": "...",
    "virtual_asset_trading_platforms": "...",
    "stablecoin_regulation": "...",
    "store_of_value_facility_rules": "...",
    "regulatory_expectations_and_licensing_triggers": "...",
    "reverse_solicitation_and_direct_market_access": "...",
    "cross_border_client_advisory": "...",
    "compliance_guidance_and_recommendations": "..."
}}

Section details:
{sections_desc}

Be SPECIFIC. Cite laws by name. For the advisory sections, give a CLEAR verdict: SERVE / SERVE WITH CONDITIONS / DECLINE."""

        try:
            messages = [
                SystemMessage(content=(
                    "You are a senior regulatory compliance analyst advising Zodia Markets. "
                    "You ONLY analyze regulations that directly affect Zodia's business: "
                    "OTC brokerage, electronic exchange, fiat-to-crypto, non-custodial trading, "
                    "cross-border institutional services. "
                    "Always cover reverse solicitation and direct market access rules. "
                    "Only reference enacted/enforced regulations. Cite specific legislation. "
                    "Give clear SERVE / SERVE WITH CONDITIONS / DECLINE verdicts. "
                    "Zodia is licensed ONLY in UK (FCA), Ireland (CBI), Abu Dhabi (ADGM), Jersey (JFSC)."
                )),
                HumanMessage(content=prompt)
            ]

            response = self.llm.invoke(messages)
            response_text = response.content

            report = self._parse_json_response(response_text)
            if report:
                report["_raw_response"] = response_text[:500]
                report["_regulation_status"] = "enacted_enforced_only"
                return report
            else:
                return {
                    "summary": response_text[:2000],
                    "high_level_risk_points": [],
                    "regulatory_framework": "See summary",
                    "virtual_asset_trading_platforms": "See summary",
                    "stablecoin_regulation": "See summary",
                    "store_of_value_facility_rules": "See summary",
                    "regulatory_expectations_and_licensing_triggers": "See summary",
                    "reverse_solicitation_and_direct_market_access": "See summary",
                    "cross_border_client_advisory": "See summary",
                    "compliance_guidance_and_recommendations": "See summary",
                    "_raw_response": response_text[:500],
                    "_parse_error": "Could not parse structured JSON"
                }

        except Exception as e:
            return self._generate_fallback_report(jurisdiction, news_articles, registration_info, str(e))

    def _parse_json_response(self, text: str) -> Optional[Dict]:
        """Extract and parse JSON from LLM response."""
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        for marker in ["```json", "```"]:
            if marker in text:
                start = text.find(marker) + len(marker)
                end = text.find("```", start)
                if end > start:
                    try:
                        return json.loads(text[start:end].strip())
                    except json.JSONDecodeError:
                        pass

        brace_start = text.find("{")
        brace_end = text.rfind("}")
        if brace_start >= 0 and brace_end > brace_start:
            try:
                return json.loads(text[brace_start:brace_end + 1])
            except json.JSONDecodeError:
                pass

        return None

    def _generate_fallback_report(
        self,
        jurisdiction: str,
        news_articles: List[Dict],
        registration_info: Optional[Dict],
        error: str = ""
    ) -> Dict:
        """Generate a basic report when LLM is unavailable."""
        news_summary = ""
        if news_articles:
            news_summary = "; ".join(a.get("title", "") for a in news_articles[:5])

        is_registered = registration_info is not None

        return {
            "summary": f"Regulatory analysis for {jurisdiction}. {f'Error: {error}' if error else 'LLM unavailable.'}",
            "high_level_risk_points": [
                f"Regulatory status in {jurisdiction} requires manual review",
                "LLM-powered analysis unavailable - basic report only"
            ],
            "regulatory_framework": f"Manual review needed for {jurisdiction}.",
            "virtual_asset_trading_platforms": "Requires LLM analysis.",
            "stablecoin_regulation": "Requires LLM analysis.",
            "store_of_value_facility_rules": "Requires LLM analysis.",
            "regulatory_expectations_and_licensing_triggers": "Requires LLM analysis.",
            "reverse_solicitation_and_direct_market_access": (
                f"UNKNOWN - Manual legal review required for {jurisdiction}. "
                "Determine if reverse solicitation is permitted and under what conditions."
            ),
            "cross_border_client_advisory": (
                f"Zodia Markets {'IS' if is_registered else 'is NOT'} licensed in {jurisdiction}. "
                + (
                    "Clients can be onboarded under the existing registration."
                    if is_registered else
                    "Before serving any client, conduct a detailed legal review "
                    "to determine if a local license is required."
                )
            ),
            "compliance_guidance_and_recommendations": (
                f"Standard onboarding applies." if is_registered else
                f"RECOMMENDATION: Seek external legal advice before onboarding clients from {jurisdiction}."
            ),
            "_news_headlines": news_summary,
            "_registration_info": registration_info,
            "_fallback": True
        }

    def format_report_markdown(self, result: Dict) -> str:
        """Format a jurisdiction result as a readable Markdown report."""
        jurisdiction = result.get("jurisdiction", "Unknown")
        report = result.get("report", {})
        reg_info = result.get("registration_info")

        lines = []
        lines.append(f"# {jurisdiction} - Zodia Markets Regulatory Intelligence")
        lines.append(f"*Generated: {result.get('timestamp', 'N/A')}*\n")

        # Registration badge
        if result.get("is_registered"):
            lines.append(f"**STATUS: REGISTERED** - {reg_info.get('entity', '')} ({reg_info.get('license_type', '')})")
            lines.append(f"Regulator: {reg_info.get('regulator', '')} | Ref: {reg_info.get('reference', '')}")
            lines.append(f"Granted: {reg_info.get('date_granted', '')} | Scope: {reg_info.get('scope', '')}\n")
        else:
            lines.append("**STATUS: NOT REGISTERED**\n")

        # 1. Summary
        lines.append("## 1. Regulatory Regime Summary")
        lines.append(report.get("summary", "Not available."))
        lines.append("")

        # 2. Risk Points
        lines.append("## 2. High-Level Risk Points for Zodia Markets")
        risks = report.get("high_level_risk_points", [])
        if isinstance(risks, list):
            for r in risks:
                lines.append(f"- {r}")
        else:
            lines.append(str(risks))
        lines.append("")

        # 3. Regulatory Framework
        lines.append("## 3. Regulatory Framework")
        lines.append(report.get("regulatory_framework", "Not available."))
        lines.append("")

        # 4. Trading Platforms
        lines.append("## 4. Virtual Asset Trading Platforms")
        lines.append(report.get("virtual_asset_trading_platforms", "Not available."))
        lines.append("")

        # 5. Stablecoin
        lines.append("## 5. Stablecoin & Fiat-Backed Token Regulation")
        lines.append(report.get("stablecoin_regulation", "Not available."))
        lines.append("")

        # 6. Store of Value
        lines.append("## 6. Store of Value Facility Rules")
        lines.append(report.get("store_of_value_facility_rules", "Not available."))
        lines.append("")

        # 7. Licensing Triggers
        lines.append("## 7. Regulatory Expectations & Licensing Triggers")
        lines.append(report.get("regulatory_expectations_and_licensing_triggers", "Not available."))
        lines.append("")

        # 8. Reverse Solicitation & Direct Market Access
        lines.append("## 8. Reverse Solicitation & Direct Market Access")
        lines.append("*Can Zodia serve clients without local license if the client approaches first?*\n")
        lines.append(report.get("reverse_solicitation_and_direct_market_access", "Not available."))
        lines.append("")

        # 9. Cross-Border Client Advisory
        lines.append("## 9. Cross-Border Client Advisory")
        lines.append(f"*Can Zodia serve a client from {jurisdiction}?*\n")
        if result.get("is_registered"):
            lines.append(f"**ZODIA IS LICENSED HERE** - {reg_info.get('entity', '')}\n")
        else:
            lines.append(f"**ZODIA IS NOT LICENSED IN {jurisdiction.upper()}**\n")
        lines.append(report.get("cross_border_client_advisory", "Not available."))
        lines.append("")

        # 10. Compliance Guidance
        lines.append("## 10. Compliance Guidance & Recommendations")
        lines.append("*Actionable advice for Zodia Markets compliance team*\n")
        lines.append(report.get("compliance_guidance_and_recommendations", "Not available."))
        lines.append("")

        # News
        news = result.get("news_articles", [])
        if news:
            lines.append("## 11. Recent News & Developments")
            for i, article in enumerate(news[:5], 1):
                lines.append(f"{i}. **{article.get('title', 'N/A')}**")
                lines.append(f"   {article.get('published_at', '')[:10]} | {article.get('source', '')}")
                lines.append(f"   {article.get('url', '')}")
            lines.append("")

        lines.append("---")
        lines.append(f"*Only enacted/enforced/final regulations. Duration: {result.get('duration_seconds', 0):.1f}s*")

        return "\n".join(lines)

    def save_report(self, result: Dict, output_dir: str = None) -> str:
        """Save a jurisdiction report to file."""
        from pathlib import Path

        if output_dir is None:
            desktop = Path.home() / "Desktop"
            output_dir = desktop / "Zodia_Markets_Regulatory_Reports"
        else:
            output_dir = Path(output_dir)

        output_dir.mkdir(parents=True, exist_ok=True)

        jurisdiction = result.get("jurisdiction", "Unknown")
        safe_name = jurisdiction.replace(" ", "_").replace("/", "_").replace("(", "").replace(")", "")
        filename = f"Zodia_{safe_name}_Regulatory_Report.md"
        filepath = output_dir / filename

        markdown = self.format_report_markdown(result)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(markdown)

        # Also save raw JSON
        json_filepath = output_dir / f"Zodia_{safe_name}_data.json"
        with open(json_filepath, "w", encoding="utf-8") as f:
            clean_result = {k: v for k, v in result.items() if not k.startswith("_")}
            json.dump(clean_result, f, indent=2, ensure_ascii=False, default=str)

        return str(filepath)
